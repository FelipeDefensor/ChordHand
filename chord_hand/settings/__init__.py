import ast
import csv
import re
from pathlib import Path
import tomli
import importlib
import shutil

from chord_hand.dirs import SETTINGS_DIR

decoder = None
encoder = None
chord_quality_to_symbol = {}
chord_quality_to_chordal_type = {}
key_to_chord_quality = {}
chord_quality_to_key = {}
default_analyses_major = {}
default_analyses_minor = {}
name_to_analytic_type = {}
analytic_type_args_to_projeto_mpb_code = {}
name_to_exporter = {}


def my_import(name):
    # adapted from https://stackoverflow.com/a/547867/15862653
    components = name.split('.')
    mod = importlib.import_module('chord_hand.' + components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def init_decoder_and_encoder():
    with OpenSettingsBinaryFile('settings.toml') as f:
        data = tomli.load(f)

    active = data['encoding']['active']
    encoder_cls, decoder_cls = my_import(data['encoding'][active][0]), my_import(data['encoding'][active][1])
    global encoder, decoder
    encoder = encoder_cls()
    decoder = decoder_cls()


def init_exporters():
    with OpenSettingsBinaryFile('settings.toml') as f:
        data = tomli.load(f)

    global name_to_exporter
    for name, (display_name, func_path)in data['exporters'].items():
        name_to_exporter[name] = (display_name, my_import(func_path))


def init_chord_symbols():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with OpenSettingsFile('chord_symbols.csv') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for raw_quality, symbol in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            chord_quality_to_symbol[quality] = symbol


def init_chordal_type():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with OpenSettingsFile('chordal_types.csv') as f:
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
    with OpenSettingsFile('keymap.csv') as f:
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
    args = [
        ('default_analyses', default_analyses_major),
        # ('default_analyses_minor', default_analyses_minor)
    ]
    for filename, default_analyses in args:
        with OpenSettingsFile(f'{filename}.csv') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip symbol line
            quality_strings = next(reader)[3:]
            qualities = [ChordQuality.from_string(s) for s in quality_strings]

            for symbol, step, chroma, *analyses in reader:
                analyses = ['Aut.' if a == '' else a for a in analyses]
                default_analyses[(int(step), int(chroma))] = dict(zip(qualities, analyses))


def init_analytic_types():
    from chord_hand.analysis import AnalyticType

    # Should be called by main, hence 'settings' must be in the path
    with OpenSettingsFile('analytic_types.csv') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        name_to_analytic_type['Aut.'] = AnalyticType('Aut.', 0, 0)
        for name, relative_step, relative_pci in reader:
            name_to_analytic_type[name] = AnalyticType(name, int(relative_step), int(relative_pci))


def init_projeto_mpb_function_codes():
    from chord_hand.analysis.modality import Modality

    def init_code(key, qualities, modality):
        qualities = qualities.split(';')

        if key not in analytic_type_args_to_projeto_mpb_code[modality]:
            analytic_type_args_to_projeto_mpb_code[modality][key] = {}
        if not qualities:
            analytic_type_args_to_projeto_mpb_code[modality][key]['*' * 10] = code
        else:
            for quality in qualities:
                analytic_type_args_to_projeto_mpb_code[modality][key][quality] = code

    analytic_type_args_to_projeto_mpb_code[Modality.MAJOR] = {}
    analytic_type_args_to_projeto_mpb_code[Modality.MINOR] = {}

    with OpenSettingsFile('projeto_mpb_function_codes.csv') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for function, analytic_type_string, step, major_chroma, minor_chroma, major_qualities, minor_qualities, code in reader:
            if major_chroma:
                key = (analytic_type_string, int(step), int(major_chroma))
                init_code(key, major_qualities, Modality.MAJOR)
            if minor_chroma:
                key = (analytic_type_string, int(step), int(minor_chroma))
                init_code(key, minor_qualities, Modality.MINOR)


class OpenSettingsFile:
    def __init__(self, name: str, mode: str = 'r'):
        self.name = name
        self.mode = mode
        self.path = SETTINGS_DIR / name

    def open_file(self):
        self.file = open(self.path, self.mode, newline='', encoding='utf-8')

    def __enter__(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(__file__).parent / 'default' / self.name, self.path)
        self.open_file()
        return self.file

    def __exit__(self, type, value, traceback):
        self.file.close()


class OpenSettingsBinaryFile(OpenSettingsFile):
    def __init__(self, name: str, mode: str = 'rb'):
        super().__init__(name, mode)

    def open_file(self):
        self.file = open(self.path, self.mode)
