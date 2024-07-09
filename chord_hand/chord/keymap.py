from chord_hand.chord.quality import ChordQuality
from chord_hand.chord.chord import NoChord
from chord_hand.chord.note import Note

CODE_TO_NOTE = {
    # top row
    "q": Note(0, 1),
    "Q": Note(0, 2),
    "w": Note(1, 1),
    "W": Note(1, 2),
    "e": Note(2, 1),
    "E": Note(2, 2),
    "r": Note(3, 1),
    "R": Note(3, 2),
    "u": Note(4, 1),
    "U": Note(4, 2),
    "i": Note(5, 1),
    "I": Note(5, 2),
    "o": Note(6, 1),
    "O": Note(6, 2),
    # home row
    "a": Note(0, 0),
    "s": Note(1, 0),
    "d": Note(2, 0),
    "f": Note(3, 0),
    "j": Note(4, 0),
    "k": Note(5, 0),
    "l": Note(6, 0),
    # bottom row
    "z": Note(0, -1),
    "Z": Note(0, -2),
    "x": Note(1, -1),
    "X": Note(1, -2),
    "c": Note(2, -1),
    "C": Note(2, -2),
    "v": Note(3, -1),
    "V": Note(3, -2),
    "m": Note(4, -1),
    "M": Note(4, -2),
    ",": Note(5, -1),
    "<": Note(5, -2),
    ".": Note(6, -1),
    ">s": Note(6, -2),
    ";": NoChord(),
    # error
    "?": Note(-1, 0),
}

NOTE_TO_CODE = {v: k for k, v in CODE_TO_NOTE.items()}

LETTER2_SPECIAL = {"?": "?"}
SLASH = "/"
TEXT_MODE = "0"

NEXT_BAR_CODE = " "
REPEAT_CHORD_CODE = "p"
