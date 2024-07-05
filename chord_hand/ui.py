from __future__ import annotations
import csv
import json

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
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

from chord_hand.cell import CELL_WIDTH, Cell
from chord_hand.chord.chord import Chord
from chord_hand.chord.decode import (
    decode,
    decode_chord_code_sequence,
)
from chord_hand.chord.encode import encode_measure
from chord_hand.crash_dialog import CrashDialog

from chord_hand.analysis.harmonic_region import HarmonicRegion

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
        self.resize(800, 240)
        self.setWindowTitle('ChordHand')
        self.chords = [[]]
        self.field_types = field_types
        self.chord_quality_to_symbol = {}
        self.cells = []
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor('#f0f0f0'))
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.init_menus()
        self.init_cells()
        self.add_widgets()
        self.position_widgets()
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

            export_mpb_action = file_menu.addAction("Export as ProjetoMPB CSV...")
            export_mpb_action.triggered.connect(self.export_as_projeto_mpb)

            export_tilia_action = file_menu.addAction("Export as TiLiA CSV...")
            export_tilia_action.triggered.connect(self.export_as_tilia)

            file_menu.addSeparator()

            to_text_action = file_menu.addAction("View as text...")
            to_text_action.triggered.connect(view_as_text_func)

        init_file_menu(
            self.load_chord_symbols_from_text,
            self.load_json_file,
            self.chord_symbols_view_as_text,
        )

        analysis_menu = self.menuBar().addMenu('Analysis')
        analyze_action = analysis_menu.addAction("Analyze")
        analyze_action.triggered.connect(self.analyze_harmonies)
        analyze_action.setShortcut('Ctrl+Shift+A')

        # init_field_menu(
        #     "Analysis",
        #     self.load_chord_symbols_from_text,
        #     self.load_chord_symbols_from_file,
        #     self.chord_symbols_to_text,
        # )
        # init_field_menu(
        #     "Region",
        #     self.load_chord_symbols_from_text,
        #     self.load_chord_symbols_from_file,
        #     self.chord_symbols_to_text,
        # )

        cell_menu = self.menuBar().addMenu("Cell")

        insert_action = cell_menu.addAction("Insert")
        insert_action.triggered.connect(self.on_insert)

        remove_action = cell_menu.addAction("Remove")
        remove_action.triggered.connect(self.on_remove)

    def init_cells(self):
        if not self.chords:
            self.cells.append(
                Cell(
                    1,
                    self.on_next_measure,
                    self.field_types,
                    self.get_active_harmonic_region,
                    chord_code="",
                )
            )
            return

        for i, chords in enumerate(self.chords):
            self.cells.append(
                Cell(
                    i + 1,
                    self.on_next_measure,
                    self.field_types,
                    self.get_active_harmonic_region,
                    chord_code=encode_measure(chords),
                )
            )

    def resize_to_fit_cells(self):
        width = min(max(self.scene.width() + 20, self.width()), 800)
        height = min(max(self.scene.height() + 80, self.height()), 800)
        self.resize(int(width), int(height))

    def on_next_measure(self, cell):
        next_index = self.cells.index(cell) + 1
        if next_index == len(self.cells):
            self.insert_cell(len(self.cells))
        self.cells[next_index].set_focus()
        self.resize_to_fit_cells()

    def get_active_harmonic_region(self, cell):
        if cell.region_code:
            return HarmonicRegion.from_string(cell.region_code)
        elif self.cells.index(cell) == 0:
            return None
        else:
            return self.get_active_harmonic_region(
                self.cells[self.cells.index(cell) - 1]
            )

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
        return " ".join([c.chord_code for c in self.cells])

    def get_chords(self):
        return decode_chord_code_sequence(self.get_chord_codes())

    def get_harmonic_regions(self):
        return [cell.region for cell in self.cells]

    def get_decoded_chords(self):
        return list(map(decode, chord) for chord in self.chords)

    def get_chord_symbols(self):
        return [list(map(str, measure)) for measure in self.get_chords()]

    def get_serialized_chords(self):
        return {i: serialize_chord_measure(bar) for i, bar in enumerate(self.get_chords())}

    def get_serialized_harmonic_regions(self):
        return {i: serialize_harmonic_region(region) for i, region in enumerate(self.get_harmonic_regions())}

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
            self.load_harmonic_regions(data["regions"])

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

    def load_chords(self, chords_data):
        for n, measure_data in chords_data.items():
            self.cells[int(n)].set_chords(list(map(Chord.from_dict, measure_data)))

    def load_harmonic_regions(self, regions_data):
        for n, region_data in regions_data.items():
            if not region_data:
                continue
            self.cells[int(n)].set_region(HarmonicRegion.from_dict(region_data))

    @staticmethod
    def get_music_title():
        return QInputDialog().getText(None, "Save", "Insert music title")

    def save_as_json(self):
        name, success = self.get_music_title()
        if not success:
            return

        path, success = QFileDialog.getSaveFileName(
            None, "Save", name.replace(" ", "_").lower() + ".json", "*.json"
        )
        if not success:
            return

        with open(path, "w") as file:
            json.dump(
                {
                    "title": name,
                    "chords": self.get_serialized_chords(),
                    "regions": self.get_serialized_harmonic_regions(),
                },
                file,
            )

    def write_csv_projeto_mpb(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            for i, measure in enumerate(self.get_chords()):
                for j, chord in enumerate(measure):
                    csv_writer.writerow([
                        chord.root.to_pitch_class(),
                        chord.bass.to_pitch_class(),
                        ord(chord.quality.to_chordal_type()[0]),
                        chord.quality.to_chordal_type()[1],
                        '',
                        '',
                        (i + 1) + j / len(measure),
                        str(chord),
                    ])

    def write_csv_tilia(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['measure', 'fraction', 'label'])
            for i, measure in enumerate(self.get_chords()):
                for j, chord in enumerate(measure):
                    csv_writer.writerow([
                        i + 1,
                        (j / len(measure)) % 1,
                        str(chord)
                    ])

    @staticmethod
    def get_file_save_path(initial, name_filter):
        return QFileDialog.getSaveFileName(
            None, 'Save', initial, name_filter
        )

    def export_as_projeto_mpb(self):
        path, success = self.get_file_save_path('Untitled.csv', '*.csv')
        if not success:
            return

        self.write_csv_projeto_mpb(path)
        pd.read_csv(path, header=None).T.to_csv(path, header=False, index=False)

    def export_as_tilia(self):
        path, success = self.get_file_save_path('Untitled.csv', '*.csv')
        if not success:
            return

        self.write_csv_tilia(path)

    @staticmethod
    def export_as_text():
        print('Exporting as text...')

    def remove_cell(self, index):
        cell = self.cells[index]
        self.scene.removeItem(cell.proxy)
        for c in self.cells[index:]:
            c.set_n(c.n - 1)
        self.position_widgets()

    def insert_cell(self, index):
        cell = Cell(
            index,
            self.on_next_measure,
            self.field_types,
            self.get_active_harmonic_region,
            chord_code="",
        )
        self.cells.insert(index, cell)
        self.add_cell_to_scene(cell)
        for cell in self.cells[index:]:
            cell.set_n(cell.n + 1)
            self.position_cell(cell)
        self.position_cell(cell)
        self.view.ensureVisible(cell.proxy)
        cell.proxy.setZValue(-cell.n)

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

    def get_active_harmonic_regions(self):
        harmonic_regions = []
        previous_region = None
        for cell in self.cells:
            if cell.region:
                harmonic_regions.append(cell.region)
                previous_region = cell.region
            else:
                harmonic_regions.append(previous_region)

        return harmonic_regions

    def analyze_harmonies(self):
        for cell in self.cells:
            cell.analyze_harmonies()


def serialize_chord(chord):
    if not chord:
        return "RepeatChord()"
    return chord.to_dict()


def serialize_harmonic_region(region):
    return region.to_dict() if region else None


def serialize_chord_measure(measure):
    return [serialize_chord(chord) for chord in measure]


def show_crash_dialog(data_dump, exc_message):
    dialog = CrashDialog(exc_message, data_dump)
    dialog.exec()
