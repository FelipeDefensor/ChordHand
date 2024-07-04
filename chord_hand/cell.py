import functools
from enum import StrEnum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QSizePolicy, QLabel, QLineEdit, QComboBox, QGridLayout

import chord_hand.analysis
import chord_hand.settings
from chord_hand import settings
from chord_hand.chord.chord import Chord
from chord_hand.chord.decode import decode_chord_code_sequence, decode, parse_multimeasure_code
from chord_hand.analysis.harmonic_region import HarmonicRegion
from chord_hand.chord.encode import encode_measure

CELL_WIDTH = 150
CELL_HEIGHT = 140


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
        self.region = ""
        self.get_active_harmonic_region = functools.partial(get_active_harmonic_region, self)
        self.harmonic_analysis = []

    def _init_widgets(self):
        self.layout = QGridLayout()

        self.widget = QFrame()
        self.widget.setFixedHeight(CELL_HEIGHT)
        self.widget.setLayout(self.layout)
        self.widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.widget.setFixedSize(CELL_WIDTH, CELL_HEIGHT)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.n_label = QLabel(str(self.n))
        self.layout.addWidget(self.n_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        self.n_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.n_label.setFixedHeight(20)

        self.init_fields()

    def init_fields(self):
        field_type_to_init_func = {
            self.FieldType.CHORD_SYMBOLS: self._init_chord_symbols_field,
            self.FieldType.HARMONIC_ANALYSIS: self._init_analysis_field,
            self.FieldType.HARMONIC_REGION: self._init_region_field,
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
        self.chord_code_line_edit.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(self.chord_code_line_edit, 1, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        self.chord_symbol_label = QLabel(
            " ".join(map(str, decode_chord_code_sequence(self.chord_code)[0]))
            if self.chord_code
            else ""
        )
        self.chord_symbol_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.chord_symbol_label.setFont(
            QFont(self.chord_symbol_label.font().family(), 16)
        )
        self.layout.addWidget(self.chord_symbol_label, 2, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

    def _init_region_field(self):
        self.region_label = QLineEdit("".join(self.region_code))
        self.region_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.region_label.textEdited.connect(
            self.on_region_field_edited
        )
        self.region_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(
            self.region_label, 3, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter
        )

    def _init_analysis_field(self):
        self.analysis_label = QLabel("".join(self.analysis_code))
        self.analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analysis_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(
            self.analysis_label, 4, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.analysis_label.setFont(QFont(self.chord_symbol_label.font().family(), 14))

    def _init_analytical_type_field(self):
        self.analytic_type_combobox = QComboBox()
        for name, analytic_type in chord_hand.settings.name_to_analytic_type.items():
            self.analytic_type_combobox.addItem(name, analytic_type)
        self.analytic_type_combobox.currentTextChanged.connect(self.on_analytic_type_combobox_edited)
        self.layout.addWidget(self.analytic_type_combobox, 4, 1, Qt.AlignmentFlag.AlignHCenter)

    def set_n(self, n):
        self.n = n
        self.n_label.setText(str(n))

    def set_analysis(self, value):
        self.harmonic_analysis = value
        self.analysis_label.setText(' '.join(list(map(str, value))))
        self.analytic_type_combobox.setCurrentText(value[0].type.name)

    def set_chords(self, chords):
        self.chords = chords
        self.chord_code = encode_measure(chords)
        self.chord_code_line_edit.setText(self.chord_code)
        self._set_chord_symbol_label(chords)

    def set_region(self, region):
        self.region = region
        self.region_label.setText(region.to_symbol())
        text_color = 'black' if region else 'red'
        self.region_label.setStyleSheet(f'color: {text_color}')

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

    def on_region_field_edited(self, text):
        if not text:
            self.region = ""
            self.region_code = ""
        if text and text[-1] == " ":
            self.chord_code_line_edit.setText(text[:-1])
            self.on_next_measure()
        else:
            self.region_code = text
            self.set_region(HarmonicRegion.from_string(text))

    def on_analytic_type_combobox_edited(self, value):
        if self.harmonic_analysis:
            self.analyze_harmonies(settings.name_to_analytic_type[value])

    def analyze_harmonies(self, analytic_type=None):
        analyses = []
        region = self.get_active_harmonic_region()
        for chord in self.chords:
            analysis = chord_hand.analysis.analyze(chord, region, analytic_type)
            print(analysis)
            analyses.append(analysis)

        self.set_analysis(analyses)

    def __repr__(self):
        return f"Cell{self.n, self.chord_code}"
