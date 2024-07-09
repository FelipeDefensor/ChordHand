from chord_hand.chord.chord import Chord, RepeatChord
from chord_hand.chord.quality import ChordQuality, CustomChordQuality
from chord_hand.chord.keymap import (
    CODE_TO_NOTE,
    NEXT_BAR_CODE,
    REPEAT_CHORD_CODE,
    SLASH,
    TEXT_MODE,
)
from chord_hand.chord.note import Note
from chord_hand.settings import key_to_chord_quality

ERROR = "ERROR"


def decode_1letter(code):
    if code == REPEAT_CHORD_CODE:
        return RepeatChord()
    if code in CODE_TO_NOTE:
        try:
            return CODE_TO_NOTE[code[0]]
        except (ValueError, KeyError, IndexError):
            print(f'Error decoding "{code}".')
            return Note(-1, 0)


def decode_3letters(code):
    root = decode_1letter(code[0])
    quality = key_to_chord_quality[code[1]]
    bass = decode_1letter(code[2])
    return Chord(root, quality, bass)


def decode_3_or_more_letters(code):
    if code[2] == SLASH:
        root = CODE_TO_NOTE[code[0]]
        try:
            quality = key_to_chord_quality[code[1]]
        except KeyError:
            quality = ChordQuality("", "", name="ERROR")
        try:
            bass = CODE_TO_NOTE[code[3]] if len(code) > 3 else None
        except KeyError:
            bass = Note(-1, 0)
        result = Chord(root, quality, bass)
        return result
    elif code[1] == TEXT_MODE:
        root = decode(code[0])
        quality = ChordQuality(
            "", "", name=code[2:]
        )
        return Chord(root, quality)
    else:
        print(f'Error decoding "{code}": 3rd char is not a valid special char.')
        return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))


def decode_2letters(code):
    try:
        return Chord(CODE_TO_NOTE[code[0]], key_to_chord_quality[code[1]])
    except (ValueError, KeyError, IndexError):
        print(f'Error decoding "{code}".')
        return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))


def decode_bracketed_code(code):
    try:
        return Chord(CODE_TO_NOTE[code[0]], CustomChordQuality(code[2:-1]))
    except (ValueError, KeyError, IndexError):
        return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))


def decode(code):
    if len(code) == 0:
        return ""
    elif len(code) == 1:
        return decode_1letter(code)
    elif len(code) > 1 and code[1] == '{':
        return decode_bracketed_code(code)
    elif len(code) == 2:
        return decode_2letters(code)
    elif len(code) == 3:
        return decode_3letters(code)
    else:
        return list(map(decode, split_code_into_chords(code)))


def split_code_into_measures(code):
    return code.split(NEXT_BAR_CODE)


def split_code_into_chords(code):
    rest = list(code)
    result = []

    while rest:
        if rest[0] == REPEAT_CHORD_CODE:
            result.append(rest.pop(0))
            continue

        root_code = rest.pop(0)
        quality_code = rest.pop(0) if rest and rest[0] != '{' else ''
        if not rest:
            result.append(root_code + quality_code)
            break
        if rest[0] == '{':
            code = root_code + rest.pop(0)  # get bracket
            while rest:
                code += rest.pop(0)
                if code[-1] == '}':
                    break
            if code[-1] != '}':
                code += '}'
            result.append(code)

        elif rest[0] == SLASH:
            rest.pop(0)  # ignore the slash
            bass_code = rest.pop(0) if rest else ''
            result.append(root_code + quality_code + bass_code)
        else:
            result.append(root_code + quality_code)

    return result


def parse_multimeasure_code(code):
    measures = split_code_into_measures(code)
    return list(map(split_code_into_chords, measures))


def decode_chord_code_sequence(text):
    text = text.replace("\n", "")
    parsed_codes = parse_multimeasure_code(text)
    decoded_measures = [list(map(decode, bar)) for bar in parsed_codes]
    for i, measure in enumerate(decoded_measures):
        for j, chord in enumerate(measure):
            # Code was just a single note, substituting for a default (major triad)
            if isinstance(chord, Note):
                decoded_measures[i][j] = Chord(chord, ChordQuality("M", "p"))

    return decoded_measures
