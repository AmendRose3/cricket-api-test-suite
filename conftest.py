import os
import pytest
from dotenv import load_dotenv # type: ignore

load_dotenv()

# ------------------------
# REST API FIXTURES
# ------------------------

@pytest.fixture(scope="session")
def project_key():
    return os.getenv("PROJECT_KEY")

@pytest.fixture(scope="session")
def base_url(project_key):
    return f"https://ants-api.sports.dev.roanuz.com/v5/cricket/{project_key}/"

@pytest.fixture
def valid_headers():
    return {
        "rs-token": os.getenv("REST_TOKEN"),
        "RZAccountKey": os.getenv("RZ_ACCOUNT_KEY"),
        "Content-Type": "application/json"
    }

@pytest.fixture
def valid_headers_1():
    return {
        "rs-token": os.getenv("REST_TOKEN_1"),
        "Content-Type": "application/json"
    }

@pytest.fixture
def invalid_headers():
    return {
        "rs-token": "INVALID",
        "RZAccountKey": os.getenv("RZ_ACCOUNT_KEY"),
    }

@pytest.fixture
def no_token_headers():
    return {
        "RZAccountKey": os.getenv("RZ_ACCOUNT_KEY"),
    }

@pytest.fixture
def empty_token_headers():
    return {
        "RZAccountKey": os.getenv("RZ_ACCOUNT_KEY"),
        "rs-token": "",
        "Content-Type": "application/json"
    }

# ------------------------
# GRAPHQL FIXTURES
# ------------------------

@pytest.fixture(scope="session")
def graphql_url():
    return "https://ants.sports.dev.roanuz.com/graphql/"

@pytest.fixture
def graphql_headers():
    return {
        "rztoken": os.getenv("GRAPHQL_TOKEN"),
        "RZAccountKey": os.getenv("GRAPHQL_ACCOUNT_KEY"),
        "RZApiKey": os.getenv("GRAPHQL_API_KEY"),
        "Content-Type": "application/json"
    }
