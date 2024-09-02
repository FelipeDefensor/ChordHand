from chord_hand.chord.chord import RepeatChord, Chord, NoChord
from chord_hand.chord.keymap import REPEAT_CHORD_CODE, CODE_TO_NOTE, SLASH, NOTE_TO_CODE
from chord_hand.chord.quality import ChordQuality
from chord_hand.chord.note import Note
from .maps import code_to_quality, quality_to_code

class ProjetoMPBDecoder:
    def decode_measure(self, code):
        if not code:
            return ''
        return list(map(self._decode_chord, self._split_code_into_chords(code)))

    @staticmethod
    def _decode_quality(code):
        return ChordQuality.from_string(code_to_quality[code])

    @staticmethod
    def _decode_note(char):
        return CODE_TO_NOTE[char]

    @staticmethod
    def _split_code_into_chords(code):
        def _get_next_chord(code):
            if len(code) <= 2:
                return code, ''

            chord = code[:2]
            for i, char in enumerate(code[2:]):
                if char == SLASH:
                    chord += char  # slash itself
                    if len(code[2:]) > i + 1:
                        chord += code[2:][i + 1]  # bass
                    break

                if not char.isnumeric():
                    break

                chord += char

            return chord, code[len(chord):]

        result = []
        if code[0] == REPEAT_CHORD_CODE:
            result.append(code[0])
            code = code[1:]
        while code:
            chord, code = _get_next_chord(code)
            result.append(chord)

        return result

    def _decode_chord(self, code):
        try:
            if len(code) == 0:
                return ""
            elif len(code) == 1:
                return self._decode_one_char(code)
            elif len(code) == 2:
                return self._decode_two_chars(code)
            else:
                return self._decode_three_or_more_chars(code)
        except (ValueError, KeyError, IndexError):
            print(f"Error decoding {code}")
            return None

    def _decode_one_char(self, char):
        if char == REPEAT_CHORD_CODE:
            return RepeatChord()
        else:
            return self._decode_note(char)

    def _decode_two_chars(self, code):
        code += '0'
        return Chord(CODE_TO_NOTE[code[0]], self._decode_quality(code[1:]))

    def _decode_three_or_more_chars(self, code):
        bass = None
        if code[-1] in CODE_TO_NOTE and code[-2] == SLASH:
            bass = self._decode_one_char(code[-1])
            code = code[:-2]
        elif code[-1] == SLASH:
            code = code[:-1]

        try:
            root = self._decode_note(code[0])
            quality = self._decode_quality(code[1:])
            return Chord(root, quality, bass)
        except (ValueError, KeyError, IndexError):
            print(f"Error decoding {code}")
            return None


class ProjetoMPBEncoder:
    def encode_measure(self, chords):
        return ''.join([self._encode_chord(chord) for chord in chords])

    @staticmethod
    def _encode_chord_quality(chord):
        if isinstance(chord, ChordQuality):
            return quality_to_code[chord]
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
