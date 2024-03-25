from chord_hand.chord.chord import NoChord, RepeatChord, Chord
from chord_hand.chord.keymap import (
    CHORD_QUALITY_TO_CODE,
    NOTE_TO_CODE,
    NEXT_CHORD,
    REPEAT_CHORD,
    SLASH,
)


def encode_chord_quality(chord):
    return CHORD_QUALITY_TO_CODE[chord]


def encode_note(note):
    return NOTE_TO_CODE[note]


def encode_chord(chord):
    if isinstance(chord, NoChord):
        return ""
    elif isinstance(chord, RepeatChord):
        return "%"
    root_str = encode_note(chord.root)
    quality_str = (
        encode_chord_quality(chord.quality)
        if not chord.quality.is_name_only()
        else chord.quality.to_string()
    )
    chord_str = f"{SLASH}{encode_note(chord.bass)}" if chord.is_inverted() else ""

    return root_str + quality_str + chord_str


def encode_measure(measure: [Chord | NoChord | RepeatChord]):
    if not measure:
        return ""
    result = (
        encode_chord(measure[0])
        if not isinstance(measure[0], RepeatChord)
        else REPEAT_CHORD
    )
    for chord in measure[1:]:
        if isinstance(chord, Chord) or isinstance(chord, NoChord):
            if not result[-1] == REPEAT_CHORD:
                result += NEXT_CHORD
            result += encode_chord(chord)
        elif isinstance(chord, RepeatChord):
            result += REPEAT_CHORD
        else:
            raise ValueError("Unrecognized chord class.")

    return result
