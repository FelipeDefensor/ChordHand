from asyncio import Protocol

from chord_hand.encoding.common import split_measure_codes_into_chord_codes
from chord_hand.chord.keymap import CODE_TO_NOTE, SLASH, TEXT_MODE, NOTE_TO_CODE
from chord_hand.chord.chord import Chord, NoChord, RepeatChord
from chord_hand.chord.note import Note
from chord_hand.chord.quality import ChordQuality, CustomChordQuality
from chord_hand.settings import key_to_chord_quality


class StandardEncoder:
    def encode_measure(self, chords):
        return ''.join([self._encode_chord(chord) for chord in chords])

    @staticmethod
    def _encode_chord_quality(chord):
        from chord_hand.settings import chord_quality_to_key

        if isinstance(chord, ChordQuality):
            return chord_quality_to_key[chord]
        else:
            # custom chord quality
            return chord.to_code()

    @staticmethod
    def _encode_note(note):
        return NOTE_TO_CODE[note]

    def _encode_chord(self, chord):
        if not chord:
            return "?"
        if isinstance(chord, NoChord):
            return ""
        elif isinstance(chord, RepeatChord):
            return "%"
        elif isinstance(chord, Note):
            return self._encode_note(chord)

        root_str = self._encode_note(chord.root)
        quality_str = self._encode_chord_quality(chord.quality)

        chord_str = f"{SLASH}{self._encode_note(chord.bass)}" if chord.is_inverted() else ""

        return root_str + quality_str + chord_str


class StandardDecoder:
    def decode_measure(self, code):
        if not code:
            return []
        return [self._decode_into_chord(c) for c in split_measure_codes_into_chord_codes(code)]

    def _decode_into_chord(self, code):
        if len(code) == 1:
            return self._decode_one_char(code)
        elif len(code) > 1 and code[1] == '{':
            return self._decode_bracketed_code(code)
        elif len(code) == 2:
            return self._decode_two_chars(code)
        elif len(code) == 3:
            return self._decode_three_chars(code)

    @staticmethod
    def _decode_one_char(code):
        # RepeatChord may be reimplemented later
        # if code == REPEAT_CHORD_CODE:
        #     return RepeatChord()

        if code in CODE_TO_NOTE:
            try:
                return CODE_TO_NOTE[code[0]]
            except (ValueError, KeyError, IndexError):
                return None

    def _decode_three_chars(self, code):
        root = self._decode_one_char(code[0])
        quality = key_to_chord_quality[code[1]]
        bass = self._decode_one_char(code[2])
        return Chord(root, quality, bass)

    def _decode_three_or_more_chars(self, code):
        if code[2] == SLASH:
            root = CODE_TO_NOTE[code[0]]
            try:
                quality = key_to_chord_quality[code[1]]
            except KeyError:
                return None
            try:
                bass = CODE_TO_NOTE[code[3]] if len(code) > 3 else None
            except KeyError:
                return None
            result = Chord(root, quality, bass)
            return result
        elif code[1] == TEXT_MODE:
            root = self._decode_into_chord(code[0])
            quality = ChordQuality(
                "", "", name=code[2:]
            )
            return Chord(root, quality)
        else:
            return None

    @staticmethod
    def _decode_two_chars(code):
        try:
            return Chord(CODE_TO_NOTE[code[0]], key_to_chord_quality[code[1]])
        except (ValueError, KeyError, IndexError):
            return None

    @staticmethod
    def _decode_bracketed_code(code):
        try:
            return Chord(CODE_TO_NOTE[code[0]], CustomChordQuality(code[2:-1]))
        except (ValueError, KeyError, IndexError):
            return Chord(Note(-1, 0), ChordQuality("", "", name="ERROR"))



