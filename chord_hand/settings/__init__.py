import ast
import csv
import re
from pathlib import Path

chord_quality_to_symbol = {}
chord_quality_to_chordal_type = {}
key_to_chord_quality = {}
chord_quality_to_key = {}


def init_chord_symbols():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path('settings', 'chord_symbols.csv'), 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) # skip header
        for raw_quality, symbol in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            chord_quality_to_symbol[quality] = symbol


def init_chordal_type():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path('settings', 'chordal_types.csv'), 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) # skip header
        for raw_quality, raw_chordal_type in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            chordal_type = ast.literal_eval(raw_chordal_type)
            chord_quality_to_chordal_type[quality] = chordal_type


def init_keymap():
    from chord_hand.chord.quality import ChordQuality

    # Should be called by main, hence 'settings' must be in the path
    with open(Path('settings', 'keymap.csv'), 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for key, raw_chord_quality in reader:
            quality_string = re.match(r'ChordQuality\((.+)\)', raw_chord_quality).group(1)
            quality = ChordQuality.from_string(quality_string)
            key_to_chord_quality[key] = quality

    chord_quality_to_key = {v: k for k, v in key_to_chord_quality.items()}
