from chord_hand.chord.chord_quality import ChordQuality
from chord_hand.chord.chord import NoChord
from chord_hand.chord.note import Note

LETTER1_TO_NOTE = {
    # top row
    "q": Note(0, 1),
    "w": Note(1, 1),
    "e": Note(2, 1),
    "r": Note(3, 1),
    "u": Note(4, 1),
    "i": Note(5, 1),
    "o": Note(6, 1),
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
    "x": Note(1, -1),
    "c": Note(2, -1),
    "v": Note(3, -1),
    "m": Note(4, -1),
    ",": Note(5, -1),
    ".": Note(6, -1),
    ";": NoChord(),
}

LETTER1_TOP_ROW = {
    "q": "C#",
    "w": "D#",
    "e": "E#",
    "r": "F#",
    "t": "",
    "y": "",
    "u": "G#",
    "i": "A#",
    "o": "B#",
    "p": "",
}
LETTER1_MID_ROW = {
    "a": "C",
    "s": "D",
    "d": "E",
    "f": "F",
    "g": "",
    "h": "",
    "j": "G",
    "k": "A",
    "l": "B",
}
LETTER1_BOT_ROW = {
    "z": "C♭",
    "x": "D♭",
    "c": "E♭",
    "v": "F♭",
    "b": "",
    "n": "",
    "m": "G♭",
    ",": "A♭",
    ".": "B♭",
    ";": "N.C.",
}
LETTER1_TO_SYMBOL = LETTER1_TOP_ROW | LETTER1_MID_ROW | LETTER1_BOT_ROW
LETTER2_NUMBER_ROW = {
    "1": "#5(maj7)",
    "!": "#11(13)",
    "2": "",
    "@": "4/7/13",
    "3": "maj7(13)",
    "#": "maj7(9,13)",
    "4": "7(13)",
    "$": "7(9,13)",
    "5": "7(b13)",
    "%": "sus2",
    "6": "m(11)",
    "^": "",
    "7": "m7(11)",
    "&": "",
    "8": "",
    "*": "",
    "9": "",
    "(": "",
    "0": "0",  # text mode
}
LETTER2_TOP_ROW = {
    "q": "#5(7)",
    "Q": "maj7(#11)",
    "w": "6(9)",
    "W": "4/7(9)",
    "e": "maj7(9)",
    "E": "maj7(9,#11)",
    "r": "7(9)",
    "R": "7(9,#11)",
    "t": "(add9)",
    "T": "(omit5)",
    "y": "m(add9)",
    "u": "m7(9)",
    "U": "",
    "i": "o7",
    "I": "",
    "o": "m6(9)",
    "O": "",
    "p": ".",  # beat separator
    "P": "",
}
LETTER2_MID_ROW = {
    "a": "#5",
    "A": "7(#11)",
    "s": "6",
    "S": "4/7",
    "d": "maj7",
    "D": "",
    "f": "7",
    "F": "7(b13)",
    "g": "",  # perfect major triad
    "G": "7(#9)",
    "h": "m",
    "H": "m(maj7)",
    "j": "m7",
    "J": "",
    "k": "o",
    "K": "",
    "l": "m6",
    "L": "",
    "ç": "",  # reserved for intra-bar separator
}
LETTER2_BOT_ROW = {
    "z": "/",
    "Z": "#11",
    "x": "6(♭9)",
    "X": "sus4",
    "c": "maj7(#11)",
    "C": "",
    "v": "7(b9)",
    "V": "7(b9,b13)",
    "b": "4/7",
    "B": "7(9,b13)",
    "n": "m(b9)",
    "N": "",
    "m": "m7(b9)",
    "M": "",
    ",": "ø",
    "<": "ø(9)",
    ".": "",
    ">": "",
}

LETTER2_TO_QUALITY = {
    # NUMBER ROW
    "1": "",
    "!": "",
    "@": "",
    "3": "",
    "#": "",
    "4": "",
    "$": "",
    "5": ChordQuality("M", "p", seventh="m", thirteenth="m", symbol="7(b13)"),
    "%": "",
    "6": "",
    "7": "",
    "0": "",
    # TOP ROW
    "q": ChordQuality("M", "A", seventh="m", symbol="#5(7)"),
    "Q": ChordQuality("M", "p", seventh="M", eleventh="A", symbol="maj7(#11)"),
    "w": ChordQuality("M", "p", ninth="M", sixth="M", symbol="6(9)"),
    "W": ChordQuality("", "p", ninth="M", fourth="p", symbol="4/7(9)"),
    "e": ChordQuality("M", "p", seventh="M", ninth="M", symbol="maj7(9)"),
    "E": ChordQuality(
        "M", "p", seventh="M", ninth="M", eleventh="A", symbol="maj7(9,#11)"
    ),
    "r": ChordQuality("M", "p", seventh="m", ninth="M", symbol="7(9)"),
    "R": ChordQuality(
        "M", "p", seventh="m", ninth="M", eleventh="A", symbol="7(9,#11)"
    ),
    "t": ChordQuality("M", "p", symbol="(add9)"),
    "T": ChordQuality("M", "", symbol="(omit5)"),
    "y": ChordQuality("m", "p", ninth="M", symbol="m(add9)"),
    "Y": "",
    "u": ChordQuality("m", "p", seventh="m", ninth="M", symbol="m7(9)"),
    "i": ChordQuality("m", "d", seventh="d", symbol="o7"),
    "o": ChordQuality("m", "p", ninth="M", sixth="m", symbol="m6(9)"),
    "p": "",
    # HOME ROW
    "a": ChordQuality("M", "A", symbol="#5"),
    "A": "",
    "s": ChordQuality("M", "p", sixth="M", symbol="6"),
    "S": ChordQuality("", "p", seventh="m", symbol="4/7"),
    "d": ChordQuality("M", "p", seventh="M", symbol="maj7"),
    "f": ChordQuality("M", "p", seventh="m", symbol="7"),
    "F": ChordQuality("M", "p", seventh="m", thirteenth="m", symbol="7(b13)"),
    "G": ChordQuality("M", "p", seventh="m", ninth="A", symbol="7(#9)"),
    "h": ChordQuality("m", "p", symbol="m"),
    "H": ChordQuality("m", "p", seventh="M", symbol="m(maj7)"),
    "j": ChordQuality("m", "p", seventh="m", symbol="m7"),
    "k": ChordQuality("m", "d", symbol="o"),
    "l": ChordQuality("m", "p", sixth="m", symbol="m6"),
    # BOTTOM ROW
    "z": "",
    "Z": ChordQuality("M", "p", eleventh="A", symbol="#11"),
    "x": ChordQuality("M", "p", ninth="m", sixth="M", symbol="6(♭9)"),
    "X": ChordQuality("", "p", symbol="sus4"),
    "c": ChordQuality("M", "p", seventh="M", eleventh="A", symbol="maj7(#11)"),
    "v": ChordQuality("M", "p", seventh="m", ninth="m", symbol="7(b9)"),
    "V": ChordQuality(
        "M", "p", seventh="m", ninth="m", thirteenth="m", symbol="7(b9,b13)"
    ),
    "b": ChordQuality("", "p", seventh="m", symbol="4/7"),
    "B": ChordQuality(
        "M", "p", seventh="m", ninth="M", thirteenth="m", symbol="7(9,b13)"
    ),
    "n": ChordQuality("m", "p", ninth="m", symbol="m(b9)"),
    "m": ChordQuality("m", "p", seventh="m", ninth="m", symbol="m7(b9)"),
    ",": ChordQuality("m", "d", seventh="m", symbol="ø"),
    "<": ChordQuality("m", "d", seventh="m", ninth="M", symbol="ø(9)"),
}

LETTER2_SPECIAL = {"?": "?"}
LETTER2_TO_SYMBOL = LETTER2_TO_QUALITY | LETTER2_SPECIAL
BAR_SEPARATOR = "|"
INTRA_BAR_SEPARATOR = "-"
BEAT_MARKER = "."
SLASH = "z"
TEXT_MODE = "0"
