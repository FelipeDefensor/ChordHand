LETTER1_TOP_ROW = {
    "q": "#I",
    "w": "#II",
    "W": "subV",
    "e": "#III",
    "r": "#IV",
    "t": "",
    "y": "",
    "u": "#V",
    "i": "#VI",
    "o": "#VII",
    "p": "",
}
LETTER1_MID_ROW = {
    "a": "I",
    "s": "II",
    "d": "III",
    "f": "IV",
    "g": "",
    "h": "",
    "j": "V",
    "k": "VI",
    "l": "VII",
}
LETTER1_BOT_ROW = {
    "z": "♭I",
    "x": "♭II",
    "c": "♭III",
    "v": "♭IV",
    "b": "",
    "n": "",
    "m": "♭V",
    ",": "♭VI",
    ".": "♭VII",
    ";": "N.C.",
}
LETTER1_TO_SYMBOL = LETTER1_TOP_ROW | LETTER1_MID_ROW | LETTER1_BOT_ROW

LETTER2_NUMBER_ROW = {
    "1": "",
    "!": "",
    "2": "",
    "@": "",
    "3": "",
    "#": "",
    "4": "",
    "$": "",
    "5": "",
    "%": "",
    "6": "",
    "^": "",
    "7": "",
    "&": "",
    "8": "",
    "*": "",
    "9": "",
    "(": "",
    "0": "0",  # text mode
}
LETTER2_TOP_ROW = {
    "q": "",
    "Q": "",
    "w": "",
    "W": "",
    "e": "",
    "E": "",
    "r": "",
    "R": "",
    "t": "",
    "T": "",
    "y": "",
    "Y": "",
    "u": "",
    "U": "",
    "i": "",
    "I": "",
    "o": "",
    "O": "",
    "p": ".",  # beat separator
    "P": "",
}
LETTER2_MID_ROW = {
    "a": "",
    "A": "",
    "s": "",
    "S": "",
    "d": "^6",
    "D": "",
    "f": "^4/6",
    "F": "",
    "g": "",  # perfect major triad
    "G": "",
    "h": "",
    "H": "",
    "j": "^2",
    "J": "",
    "k": "",
    "K": "",
    "l": "",
    "L": "",
    "ç": "",  # reserved for intra-bar separator
}
LETTER2_BOT_ROW = {
    "z": "/",
    "Z": "",
    "x": "",
    "X": "",
    "c": "",
    "C": "",
    "v": "",
    "V": "",
    "b": "3/5",
    "B": "",
    "n": "",
    "N": "",
    "m": "",
    "M": "",
    ",": "",
    "<": "",
    ".": "",
    ">": "",
}
LETTER2_SPECIAL = {"?": "?"}
LETTER2_TO_SYMBOL = (
    LETTER2_NUMBER_ROW
    | LETTER2_TOP_ROW
    | LETTER2_MID_ROW
    | LETTER2_BOT_ROW
    | LETTER2_SPECIAL
)
BAR_SEPARATOR = "|"
INTRA_BAR_SEPARATOR = "-"
BEAT_MARKER = "."
SLASH = "z"
TEXT_MODE = "0"
