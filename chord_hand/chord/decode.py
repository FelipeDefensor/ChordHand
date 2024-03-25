from chord_hand.chord.chord import Chord, RepeatChord
from chord_hand.chord.chord_quality import ChordQuality
from chord_hand.chord.keymap import (
    CODE_TO_NOTE,
    NEXT_BAR,
    NEXT_CHORD,
    REPEAT_CHORD,
    CODE_TO_CHORD_QUALITY,
    SLASH,
    TEXT_MODE,
)
from chord_hand.chord.note import Note

ERROR = "ERROR"


def decode_1letter(code):
    if code == REPEAT_CHORD:
        return RepeatChord()
    if code in CODE_TO_NOTE:
        try:
            return CODE_TO_NOTE[code[0]]
        except (ValueError, KeyError, IndexError):
            print(f'Error decoding "{code}".')
            return Note(-1, 0)


def decode_3_or_more_letters(code):
    if code[2] == SLASH:
        root = CODE_TO_NOTE[code[0]]
        try:
            quality = CODE_TO_CHORD_QUALITY[code[1]]
        except KeyError:
            quality = ChordQuality("", "", name="ERROR")
        try:
            bass = CODE_TO_NOTE[code[3]] if len(code) > 3 else None
        except KeyError:
            bass = Note(-1, 0)
        result = Chord(root, quality, bass)
        return result
    elif code[2] == TEXT_MODE:
        root_chord = decode(code[:2])
        quality = ChordQuality(
            "", "", name=CODE_TO_CHORD_QUALITY[code[1]].to_symbol() + code[3:]
        )
        return Chord(root_chord.root, quality)
    else:
        print(f'Error decoding "{code}": 3rd char is not a valid special char.')
        return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))


def decode_2letters(code):
    try:
        return Chord(CODE_TO_NOTE[code[0]], CODE_TO_CHORD_QUALITY[code[1]])
    except (ValueError, KeyError, IndexError):
        print(f'Error decoding "{code}".')
        return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))


def decode(code):
    if len(code) == 0:
        return ""
    elif len(code) == 1:
        return decode_1letter(code)
    elif len(code) == 2:
        return decode_2letters(code)
    else:
        return decode_3_or_more_letters(code)


def parse_chord_code_sequence(code_sequence):
    code = ""
    measure = []
    measures = []
    for char in code_sequence:
        code += char
        if char == NEXT_BAR:
            if code[:-1]:  # REPEAT_CHORD at end of measure
                measure.append(code[:-1])
            code = ""
            measures.append(measure)
            measure = []
        elif char == NEXT_CHORD:
            measure.append(code[:-1])
            code = ""
        elif char == REPEAT_CHORD:
            if (
                code != REPEAT_CHORD
            ):  # REPEAT_CHORD at start of measure, or consecutive REPEAT_CHORD
                measure.append(code[:-1])
            measure.append(REPEAT_CHORD)
            code = ""
    if code:
        measure.append(code)
    measures.append(measure)
    return measures


def decode_chord_code_sequence(text):
    text = text.replace("\n", "")
    parsed_codes = parse_chord_code_sequence(text)
    decoded_measures = [list(map(decode, bar)) for bar in parsed_codes]
    for i, measure in enumerate(decoded_measures):
        for j, chord in enumerate(measure):
            # Code was just a single note, substituting for a default (major triad)
            if isinstance(chord, Note):
                decoded_measures[i][j] = Chord(chord, ChordQuality("M", "p"))

    return decoded_measures
