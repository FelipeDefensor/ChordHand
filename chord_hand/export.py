from __future__ import annotations

import csv
import itertools
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog


def get_export_path(initial='Untitled', name_filter='*.txt'):
    return QFileDialog.getSaveFileName(
        None, 'Export', initial + Path(name_filter).suffix, name_filter
    )


def export_txt(data):
    path, success = get_export_path(name_filter='*.txt')
    if success:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)


def export_standard_txt(chords, regions, analyses):
    export_txt(get_standard_text_data(chords, regions, analyses))


def export_csv(data):
    path, success = get_export_path(name_filter='*.csv')
    if success:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(data)


def export_standard_csv(chords, regions, analyses):
    export_csv(get_standard_csv_data(chords, regions, analyses))


def export_tilia_csv(chords, regions, analyses):
    export_csv(get_tilia_csv_data(chords, regions, analyses))


def get_standard_text_data(chords, regions, analyses):
    data = 'CHORDS: '
    for measure in chords:
        for chord in measure:
            data += chord.to_symbol() if chord else '?' + ' '
        data += ' | '
    data += '\n'

    data += 'REGIONS: '
    prev_region = None
    for region in regions:
        if region != prev_region:
            data += region.to_symbol() + ' '
            prev_region = region
        data += ' | '
    data += '\n'

    data += 'ANALYSES: '
    for measure in analyses:
        for analysis in measure:
            data += analysis.to_symbol() + ' '
        data += ' | '

    return data


def get_standard_csv_data(chords, regions, analyses):
    # each iteration is a measure
    data = [['root', 'bass', 'quality', 'tonic', 'mode', 'analysis', 'position']]
    measure_number = 1
    for (cs, region, ans) in zip(chords, regions, analyses):
        chord_number = 0
        for chord, analysis in zip(cs, ans):
            data.append(
               [chord.root.to_symbol(), chord.bass.to_symbol(), chord.quality.to_symbol(), region.tonic.to_symbol(), region.modality.name.lower(), analysis.to_symbol(), measure_number + chord_number / len(cs)]
            )
            chord_number += 1
        measure_number += 1

    return data


def get_tilia_csv_data(chords, regions, analyses) -> list[list[str]]:
    data = [['measure', 'fraction', 'label', 'region', 'analyses']]
    for i, (cs, region, ans) in enumerate(
            itertools.zip_longest(chords, regions, analyses)):
        for j, chord in enumerate(cs):
            data.append([
                i + 1,
                str((j / len(cs)) % 1),
                chord.to_symbol() if chord else '',
                region.tonic.to_symbol() if region else '',
                " ".join([a.to_symbol() for a in ans]) if (ans and region) else '',
                ])
    return data

