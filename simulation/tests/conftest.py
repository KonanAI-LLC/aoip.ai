import requests

from tests.fixtures.api import *
from .logger import setup_logger, ContextLoggerAdapter

base_logger = setup_logger()

@pytest.fixture(scope="session")
def api_client():
    return requests.Session()


@pytest.fixture
def base_url():
    return "http://0.0.0.0:5001"


@pytest.fixture
def region():
    return "us-east-1"


@pytest.fixture(scope="function")
def test_logger():
    def _get_logger(test_id):
        logger_adapter = ContextLoggerAdapter(base_logger, {"test_id": test_id})
        return logger_adapter
    return _get_logger

