import functools
from enum import StrEnum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QSizePolicy, QLabel, QLineEdit

from chord_hand.chord.decode import decode_chord_code_sequence, decode, parse_chord_code_sequence
from chord_hand.roman_analysis.roman_analysis import str_to_mode, analyze_chord, str_to_chord

CELL_WIDTH = 200
CELL_HEIGHT = 35


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
