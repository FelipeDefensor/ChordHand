from __future__ import annotations

import csv
import itertools
from pathlib import Path

import chord_hand.settings
from chord_hand.analysis import Modality
from chord_hand.chord.chord import Chord
from chord_hand.export import export_csv


def analysis_to_projeto_mpb_code(analysis, modality):
    analytic_type = analysis.type.name, analysis.step, analysis.chroma
    qualities_to_codes = chord_hand.settings.analytic_type_args_to_projeto_mpb_code[modality].get(analytic_type, None)
    if not qualities_to_codes:
        return ''
    for quality_str, code in qualities_to_codes.items():
        if analysis.quality.match_string(quality_str):
            return code


def export_projeto_mpb_new_csv(chords, regions, analyses):
    export_csv(get_projeto_mpb_new_db_data(chords, regions, analyses))


def export_projeto_mpb_old_csv(chords, regions, analyses):
    export_csv(get_projeto_mpb_old_db_data(chords, regions, analyses))


def get_projeto_mpb_base_data(chords, regions, analyses):
    from chord_hand.chord.quality import CustomChordQuality
    from chord_hand.projeto_mpb import analysis_to_projeto_mpb_code

    rows = []
    for i, (cs, ans, region) in enumerate(
            itertools.zip_longest(chords, analyses, regions)):
        for j, (chord, analysis) in enumerate(itertools.zip_longest(cs, ans)):
            position = round((i + 1) + j / len(cs), 3)  # compasso.fração
            symbol = chord.to_symbol() if chord else ''
            region_symbol = region.to_symbol() if region else ''
            if chord and isinstance(chord, Chord):  # incomplete code will result in a Note instead
                is_quality_custom = isinstance(chord.quality, CustomChordQuality)
                row = [
                    chord.root.to_pitch_class(),  # fundamental
                    chord.bass.to_pitch_class(),  # baixo
                    chord.quality,  # qualidade
                    analysis_to_projeto_mpb_code(
                        analysis, region.modality if region_symbol else ''
                    ) if region_symbol and not is_quality_custom else '',
                    # função harmônica
                    region.tonic.to_pitch_class() if region else '',  # tônica
                    {Modality.MAJOR: 1, Modality.MINOR: 0}[region.modality] if region else '',  # modo
                    position,  # compasso.fração
                    symbol,  # símbolo
                    region_symbol,  # região
                ]
            else:
                row = ['', '', '', '', '', position, symbol, region_symbol]
            rows.append(row)

    return rows


def get_projeto_mpb_new_db_data(chords, analyses, regions):
    pmpb_path = Path(__file__).parent / 'encoding' / 'projeto_mpb'
    lex_functions = pmpb_path / 'lex-functions.csv'

    function_code_to_symbol = {}
    with open(lex_functions, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for code, symbol in reader:
            function_code_to_symbol[code] = symbol

    base_data = get_projeto_mpb_base_data(chords, analyses, regions)
    new_db_data = [[
        '',
        '',
        row[0],
        row[1],
        row[2].to_symbol(),
        function_code_to_symbol[row[3]] if row[3] else '',
        row[4],
        row[5],
        row[6]
    ]
        for row in base_data

    ]
    new_db_data.insert(0, ['corpus', 'musica', 'fundamental', 'baixo', 'cifra', 'função', 'tonica', 'modo', 'posição'])
    return new_db_data


def get_projeto_mpb_old_db_data(chords, analyses, regions):
    pmpb_path = Path(__file__).parent / 'encoding' / 'projeto_mpb'
    lex_functions = pmpb_path / 'lex-functions.csv'

    function_code_to_symbol = {}
    with open(lex_functions, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for code, symbol in reader:
            function_code_to_symbol[code] = symbol

    base_data = get_projeto_mpb_base_data(chords, analyses, regions)
    from chord_hand.chord.quality import CustomChordQuality
    old_db_data = [[
        row[0],
        row[1],
        ord(row[2].to_chordal_type()[0]) if not isinstance(row[3], CustomChordQuality) else '',
        row[2].to_chordal_type()[1] if not isinstance(row[3], CustomChordQuality) else '',
        row[3] or '',
        row[4],
        row[5],
        row[6]
    ]
        for row in base_data

    ]
    old_db_data = [*zip(*old_db_data)]  # tranpose data

    return old_db_data
