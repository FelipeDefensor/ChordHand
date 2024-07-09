from chord_hand.chord.chord import NoChord, RepeatChord, Chord
from chord_hand.chord.keymap import (
    NOTE_TO_CODE,
    REPEAT_CHORD_CODE,
    SLASH,
)
from chord_hand.chord.quality import ChordQuality


def encode_chord_quality(chord):
    from chord_hand.settings import chord_quality_to_key

    if isinstance(chord, ChordQuality):
        return chord_quality_to_key[chord]
    else:
        # custom chord quality
        return chord.to_code()


def encode_note(note):
    return NOTE_TO_CODE[note]


def encode_chord(chord):
    if isinstance(chord, NoChord):
        return ""
    elif isinstance(chord, RepeatChord):
        return "%"
    root_str = encode_note(chord.root)
    quality_str = encode_chord_quality(chord.quality)

    chord_str = f"{SLASH}{encode_note(chord.bass)}" if chord.is_inverted() else ""

    return root_str + quality_str + chord_str


def encode_measure(measure: [Chord | NoChord | RepeatChord]):
    if not measure:
        return ""
    result = (
        encode_chord(measure[0])
        if not isinstance(measure[0], RepeatChord)
        else REPEAT_CHORD_CODE
    )
    for chord in measure[1:]:
        if isinstance(chord, Chord) or isinstance(chord, NoChord):
            result += encode_chord(chord)
        elif isinstance(chord, RepeatChord):
            result += REPEAT_CHORD_CODE
        else:
            raise ValueError("Unrecognized chord class.")

    return result
