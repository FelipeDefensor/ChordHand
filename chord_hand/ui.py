from __future__ import annotations
import csv
import functools
import itertools
import json
import subprocess
import sys
import traceback
from pathlib import Path

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPalette
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QGraphicsScene,
    QGraphicsView,
    QInputDialog,
    QFileDialog,
    QDialog,
    QMessageBox,
)

from chord_hand.analysis import HarmonicAnalysis, Modality
from chord_hand.cell import CELL_WIDTH, Cell
from chord_hand.chord.chord import Chord
from chord_hand.dirs import SETTINGS_DIR
from chord_hand.encoding.common import decode_chord_code_sequence
from chord_hand.crash_dialog import CrashDialog

from chord_hand.analysis.harmonic_region import HarmonicRegion
from chord_hand.encoding.standard import StandardEncoder

LINE_LENGTH = 4
FIELD_HEIGHT = 40


def display_error(title, message):
    try:
        QMessageBox(
            QMessageBox.Icon.Critical, title, message, QMessageBox.StandardButton.Close
        ).exec()
    finally:
        print(message)


class MainWindow(QMainWindow):
    def __init__(self, field_types=(
            Cell.FieldType.CHORD_SYMBOLS, Cell.FieldType.HARMONIC_REGION, Cell.FieldType.HARMONIC_ANALYSIS,
            Cell.FieldType.ANALYTICAL_TYPE)):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle('ChordHand')
        self.chords = [[]]
        self.field_types = field_types
        self.chord_quality_to_symbol = {}
        self.cells = []
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.init_menus()
        self.init_cells()
        self.add_widgets()
        self.position_widgets()
        self.set_background_color()
        self.show()

    def init_menus(self):
        def init_file_menu(
                load_from_text_func, load_from_file_func, view_as_text_func
        ):
            file_menu = self.menuBar().addMenu("File")

            load_text_action = file_menu.addAction("Load text...")
            load_text_action.triggered.connect(load_from_text_func)

            load_text_action = file_menu.addAction("Load JSON...")
            load_text_action.triggered.connect(load_from_file_func)

            file_menu.addSeparator()

            save_action = file_menu.addAction("Save as JSON...")
            save_action.triggered.connect(self.save_as_json)

            file_menu.addSeparator()

            export_text_action = file_menu.addAction("Export as text...")
            export_text_action.triggered.connect(self.export_as_text)

            export_tilia_action = file_menu.addAction("Export as TiLiA CSV...")
            export_tilia_action.triggered.connect(self.export_as_tilia)

            file_menu.addSeparator()

            to_text_action = file_menu.addAction("View as text...")
            to_text_action.triggered.connect(view_as_text_func)

            file_menu.addSeparator()

            settings_action = file_menu.addAction("Settings...")
            settings_action.triggered.connect(self.open_settings)

        init_file_menu(
            self.load_chord_symbols_from_text,
            self.load_json_file,
            self.chord_symbols_view_as_text,
        )

        cell_menu = self.menuBar().addMenu("Cell")

        insert_action = cell_menu.addAction("Insert")
        insert_action.triggered.connect(self.on_insert)

        remove_action = cell_menu.addAction("Remove")
        remove_action.triggered.connect(self.on_remove)

        help_menu = self.menuBar().addMenu("Help")

        encoding_help_action = help_menu.addAction("Encoding")
        encoding_help_action.triggered.connect(self.on_encoding_help)

    def init_cells(self):
        if not self.chords:
            self.cells.append(
                Cell(
                    1,
                    self.on_next_measure,
                    self.update_regions,
                    self.field_types,
                    chords=[]
                )
            )
            return

        for i, chords in enumerate(self.chords):
            self.cells.append(
                Cell(
                    i + 1,
                    self.on_next_measure,
                    self.update_regions,
                    self.field_types,
                    chords=chords
                )
            )

    def set_background_color(self):
        color = self.cells[0].widget.palette().color(QPalette.ColorRole.Window)
        self.scene.setBackgroundBrush(color)

    def on_next_measure(self, cell):
        next_index = self.cells.index(cell) + 1
        if next_index == len(self.cells):
            self.insert_cell(len(self.cells))
        self.cells[next_index].set_focus()

    def update_regions(self):
        current_region = None
        for cell in self.cells:
            if cell.region and not cell.is_region_inherited:
                current_region = cell.region
            else:
                cell.set_region(current_region, inherited=True)

    def clear(self):
        for cell in self.cells.copy():
            self.cells.remove(cell)
            self.scene.removeItem(cell.proxy)

    def on_remove(self):
        n, accept = QInputDialog().getInt(
            None,
            "Remove measure",
            "Enter measure number to remove",
            min=1,
            max=len(self.cells),
        )
        if accept:
            self.remove_cell(n - 1)

    def on_insert(self):
        n, accept = QInputDialog().getInt(
            None,
            "Insert measure",
            "Insert measure before",
            min=1,
            max=len(self.cells) + 1,
        )
        if accept:
            self.insert_cell(n - 1)

    def chord_symbols_view_as_text(self):
        dialog = QDialog()
        dialog.setWindowTitle("ChordHand")
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        label = QLabel()
        label.setText(self.get_chord_codes())
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setWordWrap(True)
        layout.addWidget(label)
        dialog.exec()

    def get_chord_codes(self):
        return " ".join([c.chord_codes for c in self.cells])

    def get_chords(self):
        return [cell.chords for cell in self.cells]

    def get_regions(self):
        return [cell.region for cell in self.cells]

    def get_analyses(self):
        return [cell.harmonic_analysis for cell in self.cells]

    def get_are_analytic_types_locked(self):
        return [cell.is_analytic_type_locked for cell in self.cells]

    def get_chord_symbols(self):
        return [list(map(str, measure)) for measure in self.get_chords()]

    def get_serialized_chords(self):
        return {i: serialize_chord_list(bar) for i, bar in enumerate(self.get_chords())}

    def get_serialized_regions(self):
        return {i: serialize_region(region) for i, region in enumerate(self.get_regions())}

    def get_serialized_analyses(self):
        result = {}
        for i, (analyses, at_locked) in enumerate(zip(self.get_analyses(), self.get_are_analytic_types_locked())):
            result[i] = {
                'analyses': list(map(serialize_analysis, analyses)),
                'analytic_type_locked': at_locked
            }
        return result

    @staticmethod
    def get_file_data():
        file_name, _ = QFileDialog().getOpenFileName(filter="*.json")
        if file_name:
            with open(file_name) as f:
                data = json.load(f)
            return data

    def load_cells(self, amount):
        for _ in range(amount):
            self.insert_cell(len(self.cells))

    def load_json_file(self):
        data = self.get_file_data()
        if data:
            self.clear()
            self.load_cells(len(data['chords']))
            self.load_chords(data["chords"])
            self.load_regions(data["regions"])
            self.load_analyses(data['analyses'])

    def load_chord_symbols_from_text(self):
        result, success = QInputDialog().getMultiLineText(None, "Load text", "")
        if success:
            self.load_chord_codes(result)

    def load_chord_codes(self, text):
        self.clear()
        self.chords = decode_chord_code_sequence(text)
        self.init_cells()
        self.add_widgets()
        self.position_widgets()

    def load_chords(self, n_to_data):
        for n, data in n_to_data.items():
            self.cells[int(n)].set_chords(list(map(Chord.from_dict, data)))

    def load_regions(self, n_to_data):
        cur_data = {}
        for n, data in n_to_data.items():
            if not data:
                continue
            if data != cur_data:
                self.cells[int(n)].set_region(HarmonicRegion.from_dict(data), inherited=False)
                cur_data = data.copy()
        self.update_regions()

    def load_analyses(self, n_to_data):
        def analysis_from_data(data):
            if not data:
                return None

            return HarmonicAnalysis.from_dict(data)

        for n, data in n_to_data.items():
            if not data:
                continue
            self.cells[int(n)].set_is_analytic_type_locked(data.pop('analytic_type_locked'))
            if analyses := data['analyses']:
                self.cells[int(n)].set_analysis(list(map(analysis_from_data, analyses)))

    def save_as_json(self):
        path, success = QFileDialog.getSaveFileName(
            None, "Save", "untitled.json", "*.json"
        )
        if not success:
            return

        with open(path, "w") as file:
            json.dump(
                {
                    "chords": self.get_serialized_chords(),
                    "analyses": self.get_serialized_analyses(),
                    "regions": self.get_serialized_regions(),
                },
                file,
            )

    def write_csv_tilia(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['measure', 'fraction', 'label', 'region', 'analyses'])
            for i, (chords, region, analyses) in enumerate(itertools.zip_longest(self.get_chords(), self.get_regions(), self.get_analyses())):
                for j, chord in enumerate(chords):
                    csv_writer.writerow([
                        i + 1,
                        (j / len(chords)) % 1,
                        chord.to_symbol() if chord else '',
                        region.tonic.to_symbol() if region else '',
                        " ".join([a.to_symbol() for a in analyses]) if (analyses and region) else '',
                    ])

    def write_txt(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            f.write('CHORDS: ')
            for measure in self.get_chords():
                for chord in measure:
                    f.write(chord.to_symbol() if chord else '?' + ' ')
                f.write(' | ')
            f.write('\n')

            f.write('REGIONS: ')
            prev_region = None
            for region in self.get_regions():
                if region != prev_region:
                    f.write(region.to_symbol() + ' ')
                    prev_region = region
                f.write(' | ')
            f.write('\n')

            f.write('ANALYSES: ')
            for measure in self.get_analyses():
                for analysis in measure:
                    f.write(str(analysis) + ' ')
                f.write(' | ')

    @staticmethod
    def get_file_save_path(initial, name_filter):
        return QFileDialog.getSaveFileName(
            None, 'Save', initial, name_filter
        )

    def export_as_projeto_mpb_old_db(self):
        self.analyze_harmonies()

        path, success = self.get_file_save_path('untitled.csv', '*.csv')
        if not success:
            return

        try:
            self.write_csv_projeto_mpb(path)
            pd.read_csv(path, header=None).T.to_csv(path, header=False, index=False)
        except:
            display_error('Export error', traceback.format_exc())

    def export_as_tilia(self):
        self.analyze_harmonies()

        path, success = self.get_file_save_path('untitled.csv', '*.csv')
        if not success:
            return

        try:
            self.write_csv_tilia(path)
        except:
            display_error('Export error', traceback.format_exc())

    def export_as_text(self):
        path, success = self.get_file_save_path('untitled.txt', '*.txt')
        if not success:
            return

        self.analyze_harmonies()

        try:
            self.write_txt(path)
        except:
            display_error('Export error', traceback.format_exc())

    @staticmethod
    def open_settings():
        path = SETTINGS_DIR / 'settings.toml'

        if sys.platform == "win32":
            subprocess.Popen(["start", path.resolve()], shell=True)
        elif sys.platform == "linux":
            subprocess.Popen(["xdg-open", str(path)])  # shell=True breaks command on linux
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path.resolve()], shell=True)
        else:
            raise OSError(f"Unsupported platform: {sys.platform}")

    def remove_cell(self, index):
        cell = self.cells[index]
        self.scene.removeItem(cell.proxy)
        for c in self.cells[index:]:
            c.set_n(c.n - 1)
        self.cells.pop(index)
        self.position_widgets()

    def insert_cell(self, index):
        cell = Cell(
            index,
            self.on_next_measure,
            self.update_regions,
            self.field_types,
            chords=[]
        )
        self.cells.insert(index, cell)
        self.add_cell_to_scene(cell)
        for cell in self.cells[index:]:
            cell.set_n(cell.n + 1)
            self.position_cell(cell)
        self.position_cell(cell)
        self.view.ensureVisible(cell.proxy)
        cell.proxy.setZValue(-cell.n)
        self.update_regions()

    def add_cell_to_scene(self, cell):
        cell.proxy = self.scene.addWidget(cell.widget)

    def add_widgets(self):
        for cell in self.cells:
            self.add_cell_to_scene(cell)

    def position_cell(self, cell):
        height = cell.widget.height() + 15
        cell.widget.move(
            ((cell.n - 1) % LINE_LENGTH) * CELL_WIDTH,
            ((cell.n - 1) // LINE_LENGTH) * height,
        )

    def position_widgets(self):
        for cell in self.cells:
            self.position_cell(cell)
            cell.proxy.setZValue(-cell.n)

    def analyze_harmonies(self):
        for cell in self.cells:
            cell.analyze_harmonies()

    def on_encoding_help(self):
        class EncodingHelp(QLabel):
            def __init__(self, img1_path, img2_path):
                super().__init__()
                self.pixmap1 = QPixmap(img1_path)
                self.pixmap2 = QPixmap(img2_path)
                self.setPixmap(self.pixmap1)

            def toggle_pixmap(self):
                self.setPixmap(self.pixmap2 if self.pixmap() == self.pixmap1 else self.pixmap1)

        from chord_hand.settings import encoder
        img_path = Path(__file__).parent / 'img'
        filename = 'kb-layout-qualities-combined.png' if isinstance(encoder, StandardEncoder) else 'projeto_mpb_codes_help.png'
        widget = EncodingHelp(str(img_path / filename), '')

        self.encoding_help_window = widget
        widget.show()


class ProjetoMPBMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        projeto_mpb_menu = self.menuBar().addMenu('Projeto MPB')

        export_old_action = projeto_mpb_menu.addAction('Export as CSV (Old database)...')
        export_old_action.triggered.connect(functools.partial(self.export_as_projeto_mpb, 'old'))

        export_new_action = projeto_mpb_menu.addAction('Export as CSV (New database)...')
        export_new_action.triggered.connect(functools.partial(self.export_as_projeto_mpb, 'new'))

    def export_as_projeto_mpb(self, db_type):
        self.analyze_harmonies()

        path, success = self.get_file_save_path('untitled.csv', '*.csv')
        if not success:
            return

        write_func = {
            'old': self.write_csv_projeto_mpb_old_db,
            'new': self.write_csv_projeto_mpb_new_db
        }[db_type]

        try:
            write_func(path)
            if db_type == 'old':
                pd.read_csv(path, header=None).T.to_csv(path, header=False, index=False)
        except:
            display_error('Export error', traceback.format_exc())

    def get_projeto_mpb_data(self):
        from chord_hand.chord.quality import CustomChordQuality
        from chord_hand.projeto_mpb import analysis_to_projeto_mpb_code

        rows = []
        for i, (chords, analyses, region) in enumerate(
                itertools.zip_longest(self.get_chords(), self.get_analyses(), self.get_regions())):
            for j, (chord, analysis) in enumerate(itertools.zip_longest(chords, analyses)):
                position = round((i + 1) + j / len(chords), 3)  # compasso.fração
                symbol = chord.to_symbol() if chord else ''
                region_symbol = region.to_symbol() if region else ''
                if chord and isinstance(chord, Chord):  # incomplete code will result in a Note instead
                    is_quality_custom = isinstance(chord.quality, CustomChordQuality)
                    row = [
                        chord.root.to_pitch_class(),  # fundamental
                        chord.bass.to_pitch_class(),  # baixo
                        chord.quality if not is_quality_custom else '',  # qualidade
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

    def write_csv_projeto_mpb_new_db(self, path):
        pmpb_path = Path(__file__).parent / 'encoding' / 'projeto_mpb'
        lex_functions = pmpb_path / 'lex-functions.csv'

        function_code_to_symbol = {}
        with open(lex_functions, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            for code, symbol in reader:
                function_code_to_symbol[code] = symbol

        data = self.get_projeto_mpb_data()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['corpus', 'musica', 'fundamental', 'baixo', 'cifra', 'função', 'tonica', 'modo', 'posição'])
            for row in data:
                corpus = ''
                musica = ''
                fundamental = row[0]
                baixo = row[1]
                tipo_acordal = row[2].to_symbol()
                funcao = function_code_to_symbol[row[3]]
                tonica = row[4]
                modo = row[5]
                posicao = row[6]

                csv_writer.writerow([corpus, musica, fundamental, baixo, tipo_acordal, funcao, tonica, modo, posicao])

    def write_csv_projeto_mpb_old_db(self, path):
        from chord_hand.chord.quality import CustomChordQuality

        data = self.get_projeto_mpb_data()

        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            for row in data:
                is_quality_custom = isinstance(row[3], CustomChordQuality)

                fundamental = row[0]
                baixo = row[1]
                genus = ord(row[2].to_chordal_type()[0]) if not is_quality_custom else ''
                variante = row[2].to_chordal_type()[1] if not is_quality_custom else ''  # variante
                funcao = row[3]
                tonica = row[4]
                modo = row[5]
                posicao = row[6]

                csv_writer.writerow([fundamental, baixo, genus, variante, funcao, tonica, modo, posicao])


def serialize_chord(chord):
    if not chord:
        return "RepeatChord()"
    return chord.to_dict()


def serialize_region(region):
    return region.to_dict() if region else None


def serialize_chord_list(chords):
    return [serialize_chord(chord) for chord in chords]


def serialize_analysis(analysis):
    return analysis.to_dict() if analysis else None


def show_crash_dialog(data_dump, exc_message):
    dialog = CrashDialog(exc_message, data_dump)
    dialog.exec()
