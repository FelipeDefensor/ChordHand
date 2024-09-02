import pytest

from chord_hand import settings
from chord_hand.analysis import HarmonicAnalysis, AnalyticType, Modality
from chord_hand.chord.quality import ChordQuality
from chord_hand.projeto_mpb import analysis_to_projeto_mpb_code


class TestAnalysisToCode:
    @pytest.mark.parametrize('quality', ['Mp', 'Mpm', 'MpM', "MpMMA"])
    def test_1_major_tonality(self, quality):
        analysis = HarmonicAnalysis(
            AnalyticType('I', 0, 0),
            0,
            0,
            0,
            0,
            ChordQuality.from_string(quality)
        )
        assert analysis_to_projeto_mpb_code(analysis, Modality.MAJOR) == '1'

    @pytest.mark.parametrize('quality', ['mp', 'mpm', 'mpM'])
    def test_1_minor_tonality(self, quality):
        analysis = HarmonicAnalysis(
            AnalyticType('I', 0, 0),
            0,
            0,
            0,
            0,
            ChordQuality.from_string(quality)
        )
        assert analysis_to_projeto_mpb_code(analysis, Modality.MINOR) == '1'

    @pytest.mark.parametrize('quality', ['Mp', 'Mpm', '_p_____p_'])
    def test_54(self, quality):
        analysis = HarmonicAnalysis(
            settings.name_to_analytic_type['V'],
            0,
            0,
            0,
            0,
            ChordQuality.from_string(quality)
        )
        assert analysis_to_projeto_mpb_code(analysis, Modality.MAJOR) == '54'

    @pytest.mark.parametrize('quality', ['Mp', 'Mpm', '_p_____p_'])
    def test_55(self, quality):
        analysis = HarmonicAnalysis(
            settings.name_to_analytic_type['V'],
            1,
            0,
            0,
            0,
            ChordQuality.from_string(quality)
        )
        assert analysis_to_projeto_mpb_code(analysis, Modality.MAJOR) == '55'
