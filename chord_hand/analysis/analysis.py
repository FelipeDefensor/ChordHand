import re
from dataclasses import dataclass
from enum import StrEnum, auto

from chord_hand.chord.chord import Chord, RepeatChord
from chord_hand.chord.note import Note
from chord_hand.settings import default_analyses, name_to_analytic_type


@dataclass
class AnalyticType:
    name: str
    relative_step: int
    relative_pci: int


@dataclass
class RomanAnalysis:
    type: AnalyticType
    step: int
    chroma: int
    relative_to_step: int
    relative_to_chroma: int


NOTE_NAME_TO_STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}

STEP_TO_NOTE_NAME = {v: k for k, v in NOTE_NAME_TO_STEP.items()}

SIGN_TO_CHROMA = {"#": 1, "b": -1, "": 0}

CHROMA_TO_SIGN = {v: k for k, v in SIGN_TO_CHROMA.items()}

STEP_TO_ROMAN = {
    0: "I",
    1: "II",
    2: "III",
    3: "IV",
    4: "V",
    5: "VI",
    6: "VII",
}


def str_to_note(s) -> Note:
    if len(s) > 2:
        return Note(-1, 0)

    step = NOTE_NAME_TO_STEP[s[0]]
    if len(s) > 1 and s[1] in SIGN_TO_CHROMA:
        chroma = SIGN_TO_CHROMA[s[1]]
    else:
        chroma = 0

    return Note(step, chroma)


def str_to_chord(string):
    note = str_to_note(string[:2])
    quality = string[1:] if not note.chroma else string[2:]

    return Chord(note, quality)


def note_to_str(note):
    return STEP_TO_NOTE_NAME[note.step] + CHROMA_TO_SIGN[note.chroma]


def analyze(chord, region):
    if isinstance(chord, RepeatChord):
        return str(chord)

    if not region or not chord or chord.quality.name == 'ERROR':
        return ''
    chord_step = (chord.root.step - region.tonic.step) % 7
    chord_chroma = -(region.tonic.chroma - chord.root.chroma)
    chord_pc = chord.root.to_pitch_class()
    analytic_type = name_to_analytic_type[default_analyses[(chord_step, chord_chroma)][chord.quality]]
    target_step = (chord_step + analytic_type.relative_step) % 7
    target_pc = Note((target_step + region.tonic.step) % 7, 0).to_pitch_class()
    target_chroma = ((chord_pc - target_pc) % 12 + analytic_type.relative_pci) % 12
    if analytic_type.name == 'I':  # diatonic case
        return CHROMA_TO_SIGN[target_chroma] + STEP_TO_ROMAN[target_step] + chord.quality.to_symbol()
    else:  # other analytic types
        suffix = '/' + CHROMA_TO_SIGN[target_chroma] + STEP_TO_ROMAN[target_step] if target_step else ''
        return analytic_type.name + chord.quality.to_symbol() + suffix

