from dataclasses import dataclass
from enum import StrEnum, auto

from chord_hand.chord.chord import Chord
from chord_hand.chord.note import Note


class ModeType(StrEnum):
    MAJOR = auto()
    MINOR = auto()


class AnalyticType(StrEnum):
    DIATONIC = "d"
    SECONDARY_V = "V"
    SECONDARY_II = "II"


@dataclass
class Mode:
    center: Note
    type: ModeType = ModeType.MAJOR


NOTE_NAME_TO_STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}

STEP_TO_NOTE_NAME = {v: k for k, v in NOTE_NAME_TO_STEP.items()}

SIGN_TO_CHROMA = {"#": 1, "♭": -1, "": 0}

CHROMA_TO_SIGN = {v: k for k, v in SIGN_TO_CHROMA.items()}


def str_to_note(string):
    step = NOTE_NAME_TO_STEP[string[0]]
    if len(string) > 1 and string[1] in SIGN_TO_CHROMA:
        chroma = SIGN_TO_CHROMA[string[1]]
    else:
        chroma = 0

    return Note(step, chroma)


def str_to_chord(string):
    note = str_to_note(string[:2])
    quality = string[1:] if not note.chroma else string[2:]

    return Chord(note, quality)


def str_to_mode(string):
    center = str_to_note(string[:2])
    mode = ModeType.MINOR if string[-1] == "m" else ModeType.MAJOR

    return Mode(center, mode)


def note_to_str(note):
    return STEP_TO_NOTE_NAME[note.step] + CHROMA_TO_SIGN[note.chroma]


STEP_TO_ROMAN = {
    0: "I",
    1: "II",
    2: "III",
    3: "IV",
    4: "V",
    5: "VI",
    6: "VII",
}


def analyze_diatonic(chord, mode):
    step = STEP_TO_ROMAN[(chord.root.step - mode.center.step) % 7]
    alteration = CHROMA_TO_SIGN[-(mode.center.chroma - chord.root.chroma)]
    return alteration + step + chord.quality


def analyze_secondary_v(chord, mode):
    tonic_step = STEP_TO_ROMAN[(chord.root.step - mode.center.step + 3) % 7]
    return "V" + chord.quality + "/" + tonic_step


def analyze_secondary_ii(chord, mode):
    tonic_step = STEP_TO_ROMAN[(chord.root.step - mode.center.step - 1) % 7]
    return "II" + chord.quality + "/" + tonic_step


analytic_type_to_func = {
    AnalyticType.DIATONIC: analyze_diatonic,
    AnalyticType.SECONDARY_II: analyze_secondary_ii,
    AnalyticType.SECONDARY_V: analyze_secondary_v,
}


def analyze_chord(chord, analytic_type, mode):
    return analytic_type_to_func[analytic_type](chord, mode)
