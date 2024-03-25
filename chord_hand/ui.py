import csv
import functools
import json
import sys
from enum import StrEnum, auto

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
    QInputDialog,
    QFileDialog,
    QFrame,
    QDialog,
)

from chord_hand.chord.chord import Chord
from chord_hand.chord.decode import (
    parse_chord_code_sequence,
    decode,
    decode_chord_code_sequence,
)
from chord_hand.chord.encode import encode_measure
from chord_hand.roman_analysis.roman_analysis import (
    analyze_chord,
    str_to_chord,
    str_to_mode,
)

LINE_LENGTH = 4
CELL_WIDTH = 200
CELL_HEIGHT = 35
FIELD_HEIGHT = 40


class Cell:
    class FieldType(StrEnum):
        CHORD_SYMBOLS = auto()
        HARMONIC_ANALYSIS = auto()
        HARMONIC_REGION = auto()

    def __init__(
        self,
        n,
        on_next_measure,
        field_types,
        get_active_harmonic_region,
        chord_code="",
        analysis_code="",
        region_code="",
    ):
        self.n = n
        self.chords = []
        self.chord_code = chord_code
        self.analysis_code = analysis_code
        self.region_code = region_code
        self.on_next_measure = functools.partial(on_next_measure, self)
        self.field_types = field_types

        self._init_widgets()
        self.proxy = None
        self.harmonic_region = "%"
        self.active_harmonic_region = get_active_harmonic_region

    def _init_widgets(self):
        self.layout = QVBoxLayout()

        self.widget = QFrame()
        self.widget.setLayout(self.layout)
        self.widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.widget.setFixedSize(CELL_WIDTH, CELL_HEIGHT)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.n_label = QLabel(str(self.n))
        self.layout.addWidget(self.n_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.n_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.n_label.setFixedHeight(20)

        self.init_fields()

    def init_fields(self):
        field_type_to_init_func = {
            self.FieldType.CHORD_SYMBOLS: self._init_chord_symbols_field,
            self.FieldType.HARMONIC_ANALYSIS: self._init_harmonic_analysis_field,
            self.FieldType.HARMONIC_REGION: self._init_harmonic_region_field,
        }

        for type in self.field_types:
            field_type_to_init_func[type]()

    def _init_chord_symbols_field(self):
        self.chord_symbol_code = QLineEdit("".join(self.chord_code))
        self.chord_symbol_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chord_symbol_code.textEdited.connect(self.on_chord_symbol_code_edited)
        self.chord_symbol_code.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.chord_symbol_code.setFixedHeight(25)
        self.layout.addWidget(self.chord_symbol_code, 0, Qt.AlignmentFlag.AlignHCenter)

        self.chord_symbol_label = QLabel(
            " ".join(map(str, decode_chord_code_sequence(self.chord_code)[0]))
            if self.chord_code
            else ""
        )
        self.chord_symbol_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.chord_symbol_label.setFixedHeight(30)
        self.chord_symbol_label.setFont(
            QFont(self.chord_symbol_label.font().family(), 16)
        )
        self.layout.addWidget(self.chord_symbol_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.change_cell_height(55)

    def change_cell_height(self, amount):
        self.widget.setFixedSize(self.widget.width(), self.widget.height() + amount)

    def _init_harmonic_analysis_field(self):
        self.harmonic_analysis_code = QLineEdit("".join(self.analysis_code))
        self.harmonic_analysis_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_analysis_code.textEdited.connect(
            self.on_harmonic_analysis_field_edited
        )
        self.harmonic_analysis_code.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.harmonic_analysis_code.setFixedHeight(25)
        self.layout.addWidget(
            self.harmonic_analysis_code, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.harmonic_analysis_label = QLabel(decode(self.analysis_code))
        self.harmonic_analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_analysis_label.setFixedHeight(30)
        self.harmonic_analysis_label.setFont(
            QFont(self.harmonic_analysis_label.font().family(), 16)
        )
        self.layout.addWidget(
            self.harmonic_analysis_label, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.change_cell_height(55)

    def _init_harmonic_region_field(self):
        self.harmonic_region_code = QLineEdit("".join(self.region_code))
        self.harmonic_region_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_region_code.textEdited.connect(
            self.on_harmonic_region_field_edited
        )
        self.harmonic_region_code.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.harmonic_region_code.setFixedHeight(25)
        self.layout.addWidget(
            self.harmonic_region_code, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.harmonic_region_label = QLabel(decode(self.region_code))
        self.harmonic_region_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_region_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.harmonic_region_label.setFixedHeight(30)
        self.harmonic_region_label.setFont(
            QFont(self.harmonic_analysis_label.font().family(), 16)
        )
        self.layout.addWidget(
            self.harmonic_region_label, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.change_cell_height(55)

    def set_n(self, n):
        self.n = n
        self.n_label.setText(str(n))

    def set_focus(self):
        self.chord_symbol_code.selectAll()
        self.chord_symbol_code.setFocus()

    def on_chord_symbol_code_edited(self, text):
        if text and text[-1] == " ":
            self.chord_symbol_code.setText(text[:-1])
            self.on_next_measure()
            return
        self.chord_code = text
        try:
            codes = parse_chord_code_sequence(text)[0]
        except KeyError:
            self.chords = []
            self.chord_symbol_label.setText("ERROR")
            self.chord_symbol_label.setToolTip("ERROR")
            return

        self.chords = list(map(decode, codes))
        self.chord_symbol_label.setText(" ".join(list(map(str, self.chords))))
        self.chord_symbol_label.setToolTip(self.chord_symbol_label.text())

    def on_harmonic_region_field_edited(self, text):
        if not text:
            self.region_code = ""
            self.harmonic_region_label.setText("")
            return
        if text and text[-1] == " ":
            self.chord_symbol_code.setText(text[:-1])
            self.on_next_measure()
            return
        self.harmonic_region = str_to_mode(decode(text))
        self.harmonic_region_label.setText(decode(text))

    def on_harmonic_analysis_field_edited(self, text):
        if not text:
            self.harmonic_analysis = ""
            self.harmonic_analysis_label.setText("")
            return
        if text and text[-1] == " ":
            self.chord_symbol_code.setText(text[:-1])
            self.on_next_measure()
            return

        try:
            analysis = analyze_chord(
                str_to_chord(decode(self.chord_code)),
                text,
                self.active_harmonic_region(self),
            )
        except KeyError:
            analysis = "?"

        self.harmonic_analysis = analysis
        self.harmonic_analysis_label.setText(analysis)

    def __repr__(self):
        return f"Cell{self.n, self.chord_code}"


class MainWindow(QMainWindow):
    def __init__(self, chords: [[Chord]], field_types=(Cell.FieldType.CHORD_SYMBOLS,)):
        super().__init__()
        self.chords = chords
        self.field_types = field_types
        self.cells = []
        self.scene = QGraphicsScene()
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
            name, load_from_text_func, load_from_file_func, view_as_text_func
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

            # export_csv_action = file_menu.addAction("Export as CSV...")
            # export_csv_action.triggered.connect(self.export_as_csv)

            export_csv_action = file_menu.addAction("Export as Excel...")
            export_csv_action.triggered.connect(self.export_as_xlsx_transposed)

            file_menu.addSeparator()

            to_text_action = file_menu.addAction("View as text...")
            to_text_action.triggered.connect(view_as_text_func)

        init_file_menu(
            "Chords",
            self.load_chord_symbols_from_text,
            self.load_chord_symbols_from_file,
            self.chord_symbols_view_as_text,
        )
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

    def on_next_measure(self, cell):
        next_index = self.cells.index(cell) + 1
        if next_index == len(self.cells):
            self.insert_cell(len(self.cells))
        self.cells[next_index].set_focus()

    def get_active_harmonic_region(self, cell):
        if cell.region_code != "":
            return cell.region_code
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
            self.insert_cell(n)

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

    def get_decoded_chords(self):
        return list(map(decode, chord) for chord in self.chords)

    def get_chord_symbols(self):
        return [list(map(str, measure)) for measure in self.get_chords()]

    def get_serialized_chords(self):
        sr = [serialize_bar(i, bar) for i, bar in enumerate(self.get_chords())]
        return sr

    def get_file_data(self):
        file_name, _ = QFileDialog().getOpenFileName(filter="*.json")
        if file_name:
            with open(file_name) as f:
                data = json.load(f)
            return data

    def load_chord_symbols_from_file(self):
        data = self.get_file_data()
        if data:
            self.load_chord_symbols(data["string"])

    def load_chord_symbols_from_text(self):
        result, success = QInputDialog().getMultiLineText(None, "Load text", "")
        if success:
            self.load_chord_symbols(result)

    def load_chord_symbols(self, text):
        self.clear()
        self.chords = decode_chord_code_sequence(text)
        self.init_cells()
        self.add_widgets()
        self.position_widgets()

    def save_as_json(self):
        name, success = QInputDialog().getText(None, "Save", "Insert music title")
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
                    "chords_encoded": self.get_chord_codes(),
                    "chords_decoded": self.get_serialized_chords(),
                },
                file,
            )

    def write_to_csv(self, path):
        with open(path, 'w', newline='') as f:
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

    def get_file_save_path(self, initial, name_filter):
        return QFileDialog.getSaveFileName(
            None, 'Save', initial, name_filter
        )

    # def export_as_csv(self, path):
    #    self.write_to_csv(path)

    def export_as_xlsx_transposed(self):
        path, success = self.get_file_save_path('chords_transposed' + '.xlsx', '.xlsx')
        if not success:
            return
        self.write_to_csv(path)
        pd.read_csv(path, header=None).T.to_csv(path, header=False, index=False)

    def export_as_text(self):
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
            cell.n += 1
            self.position_cell(cell)
        self.position_cell(cell)
        self.view.ensureVisible(cell.proxy)

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


def run(args=("",)):
    app = QApplication(sys.argv)
    window = MainWindow(*args)
    try:
        app.exec()
    except Exception:
        with open("dump.txt", "w") as f:
            f.write(window.chord_symbols_view_as_text())


def serialize_chord(chord):
    if not chord:
        return "RepeatChord()"
    return chord.to_string()


def serialize_bar(number, bar):
    return number, [serialize_chord(chord) for chord in bar]
