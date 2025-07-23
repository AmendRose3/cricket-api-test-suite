import pytest

#RestAPI

@pytest.fixture(scope="session")
def project_key():
    return "RS_P_1947569226156011521"

@pytest.fixture(scope="session")
def base_url(project_key):
    return f"https://ants-api.sports.dev.roanuz.com/v5/cricket/{project_key}/"

@pytest.fixture(scope="session")
def base_url(project_key):
    return f"https://ants-api.sports.dev.roanuz.com/v5/cricket/{project_key}/"



@pytest.fixture
def valid_headers():
    return {
        "rs-token": "v5sRS_P_1947569226156011521s1948292206595018757",
        "RZAccountKey": "intern-test",
        "Content-Type": "application/json"
    }


@pytest.fixture
def invalid_headers():
    return {
        "rs-token": "INVALID",
        "RZAccountKey": "intern-test",
    }

@pytest.fixture
def no_token_headers():
    return {
        "RZAccountKey": "intern-test",
    }

@pytest.fixture
def empty_token_headers():
    return {
        "RZAccountKey": "intern-test",
        "rs-token": "", 
        "Content-Type": "application/json"
    }

#GraphQL

@pytest.fixture(scope="session")
def graphql_url():
    return "https://ants.sports.dev.roanuz.com/graphql/"



@pytest.fixture
def graphql_headers():
    return {
        "rztoken": "eyJ1c2VyX2tleSI6InpFMTk0NTM4ODM1MjAxNDYzMDkxMyIsInRva2VuIjoiN2RiZWJjNGI3YjVlZmY4MjA4MTgwNjFmOGE1ZjBlMWEyZTQ1OGM0MWZiOTVhNzc1ODEzNDRmMjEwZjVlYzgxOCIsImV4cGlyZXMiOjE3ODQxODgwMDEuMH0=",
        "RZAccountKey": "intern-test",
        "RZApiKey": "v1.3S1565340608556609537.1565340608611135489",
        "RZOperationName": "AssociationReadQuery",
        "Content-Type": "application/json"
    }

