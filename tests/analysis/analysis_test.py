import itertools

import pytest

from chord_hand.analysis import AnalyticType, analyze, Modality, CHROMA_TO_SIGN
from chord_hand.analysis.harmonic_region import HarmonicRegion
from chord_hand.chord.chord import Chord
from chord_hand.chord.note import Note
from chord_hand.chord.quality import ChordQuality

STEP_TO_ROMAN = {
    0: 'I',
    1: 'II',
    2: 'III',
    3: 'IV',
    4: 'V',
    5: 'VI',
    6: 'VII',
}

CHROMA_TO_SIGN = {
    -2: 'bb',
    -1: 'b',
    0: '',
    1: '#',
    2: '##'
}


@pytest.mark.parametrize('step,chroma', itertools.product(range(7), [-1, 0, 1]))
def test_analyses_symbol_chroma_c_major(step, chroma):
    chord = Chord(Note(step, chroma), ChordQuality('M', 'p'))
    region = HarmonicRegion(Note(0, 0), Modality.MAJOR)
    analytic_type = AnalyticType('Aut.', 0, 0)
    assert analyze(chord, region, analytic_type).to_symbol() == CHROMA_TO_SIGN[
        chroma] + STEP_TO_ROMAN[step]


@pytest.mark.parametrize('step,chroma', itertools.product(range(7), [-1, 0, 1]))
def test_analyses_symbol_chroma_e_major(step, chroma):
    scale_chromas = [0, 1, 1, 0, 0, 1, 1]
    chord = Chord(Note(step, chroma), ChordQuality('M', 'p'))
    region = HarmonicRegion(Note(2, 0), Modality.MAJOR)
    analytic_type = AnalyticType('Aut.', 0, 0)
    absolute_step = (step - 2) % 7
    assert analyze(chord, region, analytic_type).to_symbol() == CHROMA_TO_SIGN[
        chroma - scale_chromas[absolute_step]] + STEP_TO_ROMAN[absolute_step]


@pytest.mark.parametrize('step,chroma', itertools.product(range(7), [-2, -1, 0]))
def test_analyses_symbol_chroma_ab_major(step, chroma):
    scale_chromas = [-1, -1, 0, -1, -1, 0, 0]
    chord = Chord(Note(step, chroma), ChordQuality('M', 'p'))
    region = HarmonicRegion(Note(5, -1), Modality.MAJOR)
    analytic_type = AnalyticType('Aut.', 0, 0)
    absolute_step = (step - 5) % 7
    assert analyze(chord, region, analytic_type).to_symbol() == CHROMA_TO_SIGN[
        chroma - scale_chromas[absolute_step]] + STEP_TO_ROMAN[absolute_step]
