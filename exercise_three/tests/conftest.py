import pytest

def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="http://localhost:5006", help="Base URL for the API")

@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")