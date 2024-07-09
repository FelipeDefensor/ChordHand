from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING

import chord_hand.ui
from chord_hand.chord.chord import Chord, RepeatChord
from chord_hand.chord.note import Note
from chord_hand.chord.quality import ChordQuality, CustomChordQuality
from chord_hand.settings import name_to_analytic_type, default_analyses

if TYPE_CHECKING:
    from chord_hand.analysis.harmonic_region import HarmonicRegion


@dataclass
class AnalyticType:
    name: str
    relative_step: int
    relative_pci: int

    def to_dict(self):
        return self.__dict__


@dataclass
class HarmonicAnalysis:
    type: AnalyticType
    step: int
    chroma: int
    relative_to_step: int
    relative_to_chroma: int
    quality: ChordQuality

    def __post_init__(self):
        if self.relative_to_chroma == 11:
            self.relative_to_chroma = -1
        if self.relative_to_chroma == 12:
            self.relative_to_chroma = 0

    def __str__(self):
        if self.type.name == 'I':  # diatonic case
            return CHROMA_TO_SIGN[self.chroma] + STEP_TO_ROMAN[self.step] + self.quality.to_symbol()
        else:  # other analytic types
            if self.relative_to_step:
                try:
                    suffix = '/' + CHROMA_TO_SIGN[self.relative_to_chroma] + STEP_TO_ROMAN[self.relative_to_step]
                except:
                    chord_hand.ui.display_error('Analysis error', 'Error: ' + str(traceback.format_exc()))
                    suffix = ''
            else:
                suffix = ''
            return self.type.name + self.quality.to_symbol() + suffix

    def to_dict(self):
        return {
            'type': self.type.to_dict(),
            'step': self.step,
            'chroma': self.chroma,
            'relative_to_step': self.relative_to_step,
            'relative_to_chroma': self.relative_to_chroma,
            'quality': self.quality.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        is_quality_custom = data['quality'].pop('custom')
        quality = ChordQuality(**data.pop('quality')) if not is_quality_custom else CustomChordQuality(**data['quality'])
        type = AnalyticType(**data.pop('type'))
        return cls(type, **data, quality=quality)


NOTE_NAME_TO_STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
STEP_TO_NOTE_NAME = {v: k for k, v in NOTE_NAME_TO_STEP.items()}
SIGN_TO_CHROMA = {"##": 2, "#": 1, "b": -1, "bb": -2, "": 0}
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


def int_to_chroma(n):
    pc = n % 12
    return pc if pc < 8 else pc - 12


def analyze(chord: Chord, region: HarmonicRegion, analytic_type: AnalyticType | None = None):
    if isinstance(chord, RepeatChord):
        return str(chord)

    if not region or not chord or chord.quality.name == 'ERROR' or isinstance(chord.quality, CustomChordQuality):
        return None
    chord_step = (chord.root.step - region.tonic.step) % 7
    chord_chroma = -(region.tonic.chroma - chord.root.chroma)
    chord_pc = chord.root.to_pitch_class()
    if not analytic_type:
        analytic_type = name_to_analytic_type[
            default_analyses[(chord_step, chord_chroma)].get(
                chord.quality, 'I'
            )
        ]
    target_step = (chord_step + analytic_type.relative_step) % 7
    target_pc = Note(region.tonic.step, 0).to_pitch_class() % 12 + Note(target_step, 0).to_pitch_class() % 12
    target_chroma = int_to_chroma((chord_pc - target_pc) % 12 + analytic_type.relative_pci)
    analysis = HarmonicAnalysis(analytic_type, chord_step, chord_chroma, target_step, target_chroma, chord.quality)
    return analysis
