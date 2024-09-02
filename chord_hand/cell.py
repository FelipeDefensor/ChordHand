import functools
from enum import StrEnum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QSizePolicy, QLabel, QLineEdit, QComboBox, QGridLayout, QCheckBox, QHBoxLayout

import chord_hand.analysis
import chord_hand.settings
from chord_hand import settings
from chord_hand.analysis import Modality, HarmonicAnalysis
from chord_hand.chord.chord import Chord
from chord_hand.analysis.harmonic_region import HarmonicRegion
from chord_hand.chord.note import Note

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
            update_other_cell_regions,
            field_types,
            chords=list[Chord],
    ):
        from chord_hand.settings import encoder

        self.n = n
        self.chords = chords
        self.chord_codes = encoder.encode_measure(self.chords)
        self.analysis_code = ''
        self.region_code = ''
        self.on_next_measure = functools.partial(on_next_measure, self)
        self.field_types = field_types

        self._init_widgets()
        self.proxy = None
        self.region = None
        self.update_other_cell_regions = update_other_cell_regions
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
        self.chord_codes_line_edit = QLineEdit(self.chord_codes)
        self.chord_codes_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chord_codes_line_edit.textEdited.connect(self.on_chord_symbol_code_edited)
        self.chord_codes_line_edit.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(self.chord_codes_line_edit, 1, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        self.chord_symbol_label = QLabel(" ".join([c.to_symbol() for c in self.chords]))
        self.chord_symbol_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.chord_symbol_label.setFont(
            QFont(self.chord_symbol_label.font().family(), 16)
        )
        self.layout.addWidget(self.chord_symbol_label, 2, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

    def _init_region_field(self):
        self.region_tonic_combobox = QComboBox()
        self.region_tonic_combobox.addItems(['', 'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'])
        self.region_tonic_combobox.activated.connect(self.on_region_tonic_activated)
        self.region_modality_combobox = QComboBox()
        self.region_modality_combobox.addItems(['', 'major', 'minor'])
        self.region_modality_combobox.activated.connect(self.on_region_modality_activated)
        self.region_layout = QHBoxLayout()
        self.region_layout.addWidget(self.region_tonic_combobox)
        self.region_layout.addWidget(self.region_modality_combobox)
        self.region_tonic_combobox.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.region_modality_combobox.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addLayout(
            self.region_layout, 3, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter
        )

    def _init_analysis_field(self):
        self.analysis_label = QLabel("".join(self.analysis_code))
        self.analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analysis_label.setFixedHeight(self.LINE_EDIT_HEIGHT)
        self.layout.addWidget(
            self.analysis_label, 4, 0, 2, 1, Qt.AlignmentFlag.AlignHCenter
        )
        self.analysis_label.setFont(QFont(self.chord_symbol_label.font().family(), 14))

    def _init_analytical_type_field(self):
        self.analytic_type_combobox = QComboBox()
        for name, analytic_type in chord_hand.settings.name_to_analytic_type.items():
            self.analytic_type_combobox.addItem(name, analytic_type)
        self.analytic_type_combobox.currentTextChanged.connect(self.on_analytic_type_combobox_edited)
        self.layout.addWidget(self.analytic_type_combobox, 4, 1, Qt.AlignmentFlag.AlignHCenter)

        self.analytical_type_lock_checkbox = QCheckBox('Lock')
        self.layout.addWidget(self.analytical_type_lock_checkbox, 5, 1, Qt.AlignmentFlag.AlignHCenter)

    def set_n(self, n):
        self.n = n
        self.n_label.setText(str(n))

    def set_analysis(self, analyses: list[HarmonicAnalysis] | None):
        if analyses is None:
            self.harmonic_analysis = []
            self.analysis_label.setText('')
            return

        def get_label(analysis):
            if not analysis:
                return '-'
            return analysis.to_symbol()

        self.harmonic_analysis = analyses
        self.analysis_label.setText(' '.join([get_label(x) for x in analyses]))
        if analyses and analyses[0]:
            self.analytic_type_combobox.setCurrentText(analyses[0].type.name)

    def set_is_analytic_type_locked(self, value):
        self.analytical_type_lock_checkbox.setChecked(value)

    def set_chords(self, chords):
        from chord_hand.settings import encoder

        self.chords = chords
        self.chord_codes = encoder.encode_measure(self.chords)
        self.chord_codes_line_edit.setText(self.chord_codes)
        self._set_chord_symbol_label(chords)

    def set_region(self, region: HarmonicRegion | None, inherited: bool):
        self.region = region
        self.is_region_inherited = inherited
        self.analyze_harmonies()
        if not inherited:
            self.region_tonic_combobox.setCurrentText(region.tonic.to_symbol() if region else '')
            self.region_modality_combobox.setCurrentText(region.modality.name.lower() if region else '')

    def set_focus(self):
        self.chord_codes_line_edit.selectAll()
        self.chord_codes_line_edit.setFocus()

    def _set_chord_symbol_label(self, chords: list[Chord]):
        def to_label(chord):
            if chord is None or chord.to_symbol() is None:
                return '?'
            elif (symbol := chord.to_symbol()) is None:
                return '?'
            else:
                return symbol
        self.chord_symbol_label.setText(" ".join(list(map(to_label, chords))))
        self.chord_symbol_label.setToolTip(self.chord_symbol_label.text())
        if self.region:
            self.analyze_harmonies()

    def on_chord_symbol_code_edited(self, text):
        if not text:
            self.chord_codes = ""
            self.chord_symbol_label.setText("")
            self.chord_symbol_label.setToolTip("")
            self.chord_codes_line_edit.setText("")
            return
        elif text and text[-1] == " ":
            self.chord_codes_line_edit.setText(text[:-1])
            self.on_next_measure()
            return

        self.chord_codes = text
        try:
            self.chords = chord_hand.settings.decoder.decode_measure(text)
        except ValueError:
            self.chords = []
            self.chord_symbol_label.setText("ERROR")
            self.chord_symbol_label.setToolTip("ERROR")
            return

        self._set_chord_symbol_label(self.chords)

    def on_region_tonic_activated(self, _):
        text = self.region_tonic_combobox.currentText()
        if not text:
            self.region_code = ""
            self.set_region(None, inherited=False)
            self.update_other_cell_regions()
            return

        self.region_code = text

        tonic_step = chord_hand.analysis.NOTE_NAME_TO_STEP[text[0]]
        tonic_chroma = chord_hand.analysis.SIGN_TO_CHROMA[text[1]] if len(text) > 1 else 0
        tonic = Note(tonic_step, tonic_chroma)

        modality_str = self.region_modality_combobox.currentText()
        if not modality_str:
            self.region_modality_combobox.setCurrentText('major')
            modality_str = 'major'
        modality = Modality.MINOR if modality_str == 'minor' else Modality.MAJOR

        self.set_region(HarmonicRegion(tonic, modality), inherited=False)
        self.update_other_cell_regions()

    def on_region_modality_activated(self, _):
        text = self.region_modality_combobox.currentText()
        if not text:
            self.region_code = ""
            self.set_region(None, inherited=False)
            self.update_other_cell_regions()
            return

        self.region_code = text
        modality = Modality.MINOR if text == 'minor' else Modality.MAJOR

        if not self.region_tonic_combobox.currentText():
            return

        self.set_region(HarmonicRegion(self.region.tonic, modality), inherited=False)
        self.update_other_cell_regions()

    def on_analytic_type_combobox_edited(self, value):
        if self.harmonic_analysis:
            self.analyze_harmonies(settings.name_to_analytic_type[value])

    @property
    def is_analytic_type_locked(self):
            return self.analytical_type_lock_checkbox.checkState() == Qt.CheckState.Checked

    def analyze_harmonies(self, analytic_type=None):
        if self.is_analytic_type_locked:
            analytic_type = self.analytic_type_combobox.currentData()
        analyses = []
        if not self.region:
            self.set_analysis(None)
            return
        for chord in self.chords:
            analysis = chord_hand.analysis.analyze(chord, self.region, analytic_type)
            analyses.append(analysis)

        self.set_analysis(analyses)

    def __repr__(self):
        return f"Cell{self.n, self.chord_codes}"
