import sys
import traceback

from PyQt6.QtWidgets import QApplication

import chord_hand.settings
from chord_hand import ui
from chord_hand.ui import MainWindow


def main():
    def handle_exception(type, value, tb):
        exc_message = ''.join(traceback.format_exception(type, value, tb))
        ui.show_crash_dialog(mw.get_chord_codes(), exc_message)
        print(exc_message)
        print(mw.get_chord_codes())
        app.exit(1)

    chord_hand.settings.init_chord_symbols()
    chord_hand.settings.init_chordal_type()
    chord_hand.settings.init_keymap()
    chord_hand.settings.init_default_analyses()
    chord_hand.settings.init_analytical_types()

    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.excepthook = handle_exception
    app.exec()


if __name__ == "__main__":
    main()
