import sys
import traceback

from PyQt6.QtWidgets import QApplication

from chord_hand import ui
from chord_hand.ui import ProjetoMPBMainWindow, MainWindow
from chord_hand.settings import init_decoder_and_encoder, init_chord_symbols, init_chordal_type, init_keymap, \
    init_default_analyses, init_analytic_types, init_settings_folder, init_projeto_mpb_function_codes


def init_settings():
    init_settings_folder()
    init_decoder_and_encoder()
    init_chord_symbols()
    init_chordal_type()
    init_keymap()
    init_default_analyses()
    init_analytic_types()
    init_projeto_mpb_function_codes()


def main():
    def handle_exception(type, value, tb):
        exc_message = ''.join(traceback.format_exception(type, value, tb))
        ui.show_crash_dialog(mw.get_chord_codes(), exc_message)
        print(exc_message)
        print(mw.get_chord_codes())
        app.exit(1)

    init_settings()

    app = QApplication(sys.argv)
    mw = ProjetoMPBMainWindow()
    sys.excepthook = handle_exception
    app.exec()


if __name__ == "__main__":
    main()
