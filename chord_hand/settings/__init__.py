import ast
import csv
import re
from pathlib import Path

chord_quality_to_symbol = {}
chord_quality_to_chordal_type = {}
key_to_chord_quality = {}
chord_quality_to_key = {}
default_analyses = {}
name_to_analytic_type = {}
analytic_type_args_to_projeto_mpb_code = {}


def init_chord_symbols():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path(__file__).parent / 'chord_symbols.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for raw_quality, symbol in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            chord_quality_to_symbol[quality] = symbol


def init_chordal_type():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path(__file__).parent / 'chordal_types.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for raw_quality, raw_chordal_type in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            chordal_type = ast.literal_eval(raw_chordal_type)
            chord_quality_to_chordal_type[quality] = chordal_type


def init_keymap():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path(__file__).parent / 'keymap.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for key, raw_chord_quality in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_chord_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            key_to_chord_quality[key] = quality

    global chord_quality_to_key
    chord_quality_to_key = {v: k for k, v in key_to_chord_quality.items()}


def init_default_analyses():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path(__file__).parent / 'default_analyses_major.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip symbol line
        quality_strings = next(reader)[3:]
        qualities = [ChordQuality.from_string(s) for s in quality_strings]

        for symbol, step, chroma, *analyses in reader:
            analyses = ['I' if a == '' else a for a in analyses]
            default_analyses[(int(step), int(chroma))] = dict(zip(qualities, analyses))


def init_analytical_types():
    from chord_hand.analysis import AnalyticType

    # Should be called by main, hence 'settings' must be in the path
    with open(Path(__file__).parent / 'analytic_types.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        name_to_analytic_type['I'] = AnalyticType('I', 0, 0)
        for name, relative_step, relative_pci in reader:
            name_to_analytic_type[name] = AnalyticType(name, int(relative_step), int(relative_pci))


def init_projeto_mpb_function_codes():
    from chord_hand.analysis.harmonic_region import Modality

    analytic_type_args_to_projeto_mpb_code[Modality.MAJOR] = {}
    analytic_type_args_to_projeto_mpb_code[Modality.MINOR] = {}

    with open(Path(__file__).parent / 'projeto_mpb_function_codes.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for function, analytic_type_string, step, major_chroma, minor_chroma, major_qualities, minor_qualities, code in reader:
            # proccess major
            key = (analytic_type_string, int(step), int(major_chroma))

            if key not in analytic_type_args_to_projeto_mpb_code[Modality.MAJOR]:
                analytic_type_args_to_projeto_mpb_code[Modality.MAJOR][key] = {}
                analytic_type_args_to_projeto_mpb_code[Modality.MINOR][key] = {}

            major_qualities = major_qualities.split(';')

            if not major_qualities:
                analytic_type_args_to_projeto_mpb_code[Modality.MAJOR][key]['*' * 10] = code
            else:
                for quality in major_qualities:
                    analytic_type_args_to_projeto_mpb_code[Modality.MAJOR][key][quality] = code
