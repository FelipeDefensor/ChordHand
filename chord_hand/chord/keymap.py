from chord_hand.chord.chord_quality import ChordQuality
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

CODE_TO_CHORD_QUALITY = {
    # NUMBER ROW
    "1": ChordQuality("M", "A", "M"),
    "!": ChordQuality("M", "p", eleventh="A", thirteenth="M"),
    "@": ChordQuality("", "p", "m", thirteenth="M", fourth="p"),
    "3": ChordQuality("M", "p", "M", thirteenth="M"),
    "#": ChordQuality("M", "p", "M", ninth="M", thirteenth="M"),
    "4": ChordQuality("M", "p", "m", thirteenth="M"),
    "$": ChordQuality("M", "p", "m", ninth="M", thirteenth="M"),
    "5": ChordQuality("M", "p", seventh="m", thirteenth="m"),
    "%": ChordQuality("", "p", second="M"),
    "6": ChordQuality("m", "p", eleventh="p"),
    "7": ChordQuality("m", "p", "m", eleventh="p"),
    # TOP ROW
    "q": ChordQuality("M", "A", seventh="m"),
    "Q": ChordQuality("M", "p", seventh="M", eleventh="A"),
    "w": ChordQuality("M", "p", ninth="M", sixth="M"),
    "W": ChordQuality("", "p", ninth="M", fourth="p"),
    "e": ChordQuality("M", "p", seventh="M", ninth="M"),
    "E": ChordQuality("M", "p", seventh="M", ninth="M", eleventh="A"),
    "r": ChordQuality("M", "p", seventh="m", ninth="M"),
    "R": ChordQuality("M", "p", seventh="m", ninth="M", eleventh="A"),
    "t": ChordQuality("M", "p", ninth="M"),
    "T": ChordQuality("M", ""),
    "y": ChordQuality("m", "p", ninth="M"),
    "u": ChordQuality("m", "p", seventh="m", ninth="M"),
    "i": ChordQuality("m", "d", seventh="d"),
    "o": ChordQuality("m", "p", ninth="M", sixth="m"),
    # HOME ROW
    "a": ChordQuality("M", "A"),
    "A": ChordQuality("M", "p", "m", eleventh="A"),
    "s": ChordQuality("M", "p", sixth="M"),
    "S": ChordQuality("", "p", seventh="m"),
    "d": ChordQuality("M", "p", seventh="M"),
    "f": ChordQuality("M", "p", seventh="m"),
    "F": ChordQuality("M", "p", seventh="m", thirteenth="m"),
    "g": ChordQuality("M", "p"),
    "G": ChordQuality("M", "p", seventh="m", ninth="A"),
    "h": ChordQuality("m", "p"),
    "H": ChordQuality("m", "p", seventh="M"),
    "j": ChordQuality("m", "p", seventh="m"),
    "k": ChordQuality("m", "d"),
    "l": ChordQuality("m", "p", sixth="m"),
    # BOTTOM ROW
    "Z": ChordQuality("M", "p", eleventh="A"),
    "x": ChordQuality("M", "p", ninth="m", sixth="M"),
    "X": ChordQuality("", "p"),
    "c": ChordQuality("M", "p", seventh="M", eleventh="A"),
    "v": ChordQuality("M", "p", seventh="m", ninth="m"),
    "V": ChordQuality("M", "p", seventh="m", ninth="m", thirteenth="m"),
    "b": ChordQuality("", "p", seventh="m"),
    "B": ChordQuality("M", "p", seventh="m", ninth="M", thirteenth="m"),
    "n": ChordQuality("m", "p", ninth="m"),
    "m": ChordQuality("m", "p", seventh="m", ninth="m"),
    ",": ChordQuality("m", "d", seventh="m"),
    "<": ChordQuality("m", "d", seventh="m", ninth="M"),
}

CHORD_QUALITY_TO_CODE = {v: k for k, v in CODE_TO_CHORD_QUALITY.items()}

LETTER2_SPECIAL = {"?": "?"}
SLASH = "z"
TEXT_MODE = "0"

NEXT_BAR = " "
REPEAT_CHORD = "p"
NEXT_CHORD = "ç"
