from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame


class CrashDialog(QDialog):
    def __init__(self, exception_info, chord_codes):
        super().__init__()
        self.exception_info = exception_info
        self.chord_codes = chord_codes
        self.setWindowTitle('Error')
        self._setup_widgets()

    def _setup_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        sorry_label = QLabel('ChordHand has crashed with the following error:')
        sorry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exc_info_text_edit = QLabel(self.exception_info)
        exc_info_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        exc_info_text_edit.setFrameShadow(QFrame.Shadow.Sunken)
        exc_info_text_edit.setFrameShape(QFrame.Shape.Box)
        dump_label = QLabel('Here are the chord codes you were working on:')
        dump_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chord_codes_text_edit = QLabel(self.chord_codes)
        chord_codes_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        chord_codes_text_edit.setFrameShadow(QFrame.Shadow.Sunken)
        chord_codes_text_edit.setFrameShape(QFrame.Shape.Box)

        layout.addWidget(sorry_label)
        layout.addWidget(exc_info_text_edit)
        layout.addWidget(dump_label)
        layout.addWidget(chord_codes_text_edit)

        layout.setSpacing(5)