import functools
from enum import StrEnum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QSizePolicy, QLabel, QLineEdit, QHBoxLayout, QComboBox

import chord_hand.settings
from chord_hand.chord.chord import Chord
from chord_hand.chord.decode import decode_chord_code_sequence, decode, parse_multimeasure_code
from chord_hand.analysis.harmonic_region import HarmonicRegion
from chord_hand.chord.encode import encode_measure

CELL_WIDTH = 200
CELL_HEIGHT = 35


class Cell:
    LINE_EDIT_HEIGHT = 20

    class FieldType(StrEnum):
        CHORD_SYMBOLS = auto()
        HARMONIC_ANALYSIS = auto()
        HARMONIC_REGION = auto()
        ANALYTICAL_TYPE = auto()

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
        self.harmonic_region = ""
        self.active_harmonic_region = get_active_harmonic_region
        self.harmonic_analyses = []

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
            self.FieldType.ANALYTICAL_TYPE: self._init_analytical_type_field,
        }

        for type in self.field_types:
            field_type_to_init_func[type]()

    def change_cell_height(self, amount):
        self.widget.setFixedSize(self.widget.width(), self.widget.height() + amount)

    def _init_chord_symbols_field(self):
        self.chord_code_line_edit = QLineEdit("".join(self.chord_code))
        self.chord_code_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chord_code_line_edit.textEdited.connect(self.on_chord_symbol_code_edited)
        self.chord_code_line_edit.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.chord_code_line_edit.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(self.chord_code_line_edit, 0, Qt.AlignmentFlag.AlignHCenter)

        self.chord_symbol_label = QLabel(
            " ".join(map(str, decode_chord_code_sequence(self.chord_code)[0]))
            if self.chord_code
            else ""
        )
        self.chord_symbol_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.chord_symbol_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.chord_symbol_label.setFont(
            QFont(self.chord_symbol_label.font().family(), 16)
        )
        self.layout.addWidget(self.chord_symbol_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.change_cell_height(55)

    def _init_harmonic_analysis_field(self):
        self.harmonic_analysis_layout = QHBoxLayout()
        self.harmonic_analysis_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.harmonic_analysis_layout)
        self.harmonic_analysis_line_edit = QLabel("".join(self.analysis_code))
        self.harmonic_analysis_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_analysis_line_edit.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.harmonic_analysis_line_edit.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.harmonic_analysis_layout.addWidget(
            self.harmonic_analysis_line_edit, 3, Qt.AlignmentFlag.AlignHCenter
        )

    def _init_harmonic_region_field(self):
        self.harmonic_region_label = QLineEdit("".join(self.region_code))
        self.harmonic_region_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.harmonic_region_label.textEdited.connect(
            self.on_harmonic_region_field_edited
        )
        self.harmonic_region_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.harmonic_region_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(
            self.harmonic_region_label, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.change_cell_height(55)

    def _init_analytical_type_field(self):
        self.analytical_type_combobox = QComboBox()
        for name, analytic_type in chord_hand.settings.name_to_analytic_type.items():
            self.analytical_type_combobox.addItem(name, analytic_type)
        self.harmonic_analysis_layout.addWidget(self.analytical_type_combobox, 1, Qt.AlignmentFlag.AlignHCenter)

    def set_n(self, n):
        self.n = n
        self.n_label.setText(str(n))

    def set_harmonic_analysis(self, value):
        self.harmonic_analysis = value
        self.harmonic_analysis_line_edit.setText(value)

    def set_chords(self, chords):
        self.chords = chords
        self.chord_code = encode_measure(chords)
        self.chord_code_line_edit.setText(self.chord_code)
        self._set_chord_symbol_label(chords)

    def set_harmonic_region(self, region):
        self.harmonic_region_label.setText(region.to_symbol())
        if not region:
            self.harmonic_region_label.setStyleSheet('color: red')
            self.harmonic_region = ''
            return
        self.harmonic_region_label.setStyleSheet('color: black')
        self.harmonic_region = region

    def set_focus(self):
        self.chord_code_line_edit.selectAll()
        self.chord_code_line_edit.setFocus()

    def _set_chord_symbol_label(self, chords: list[Chord]):
        self.chord_symbol_label.setText(" ".join(list(map(str, chords))))
        self.chord_symbol_label.setToolTip(self.chord_symbol_label.text())

    def on_chord_symbol_code_edited(self, text):
        if text and text[-1] == " ":
            self.chord_code_line_edit.setText(text[:-1])
            self.on_next_measure()
            return
        self.chord_code = text
        try:
            codes = parse_multimeasure_code(text)[0]
        except KeyError:
            self.chords = []
            self.chord_symbol_label.setText("ERROR")
            self.chord_symbol_label.setToolTip("ERROR")
            return

        self.chords = list(map(decode, codes))
        self._set_chord_symbol_label(self.chords)

    def on_harmonic_region_field_edited(self, text):
        if not text:
            self.region_code = ""
            return
        if text and text[-1] == " ":
            self.chord_code_line_edit.setText(text[:-1])
            self.on_next_measure()
            return

        self.set_harmonic_region(HarmonicRegion.from_string(text))

    def __repr__(self):
        return f"Cell{self.n, self.chord_code}"
