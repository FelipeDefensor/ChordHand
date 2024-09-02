import pytest

from chord_hand.main import init_settings


@pytest.fixture(scope='session', autouse=True)
def setup_session():
   init_settings()
