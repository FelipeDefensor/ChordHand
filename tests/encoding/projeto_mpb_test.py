import pytest

from chord_hand.chord.note import Note
from chord_hand.encoding.projeto_mpb import ProjetoMPBDecoder, quality_to_code, code_to_quality


@pytest.mark.parametrize('quality', list(quality_to_code))
def test_quality_has_symbol(quality):
    assert quality.to_symbol() is not None


class TestDecoder:
    @property
    def decoder(self):
        return ProjetoMPBDecoder()

    @pytest.mark.parametrize('code', list(code_to_quality))
    def test_decode(self, code):
        assert self.decoder.decode_measure(code)

    def test_with_bass(self):
        chord = self.decoder.decode_measure('aZ0/d')[0]
        assert chord.root == Note(0, 0)
        assert chord.bass == Note(2, 0)

    def test_with_bass_followed_by_another_code(self):
        chord1, chord2 = self.decoder.decode_measure('aZ0/dsZ0')
        assert chord1.root == Note(0, 0)
        assert chord1.bass == Note(2, 0)
        assert chord2.root == Note(1, 0)
