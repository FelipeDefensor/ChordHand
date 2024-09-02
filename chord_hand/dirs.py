import platformdirs
from pathlib import Path

APP_NAME = 'ChordHand'
APP_AUTHOR = 'ChordHand'

SETTINGS_DIR = Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))
