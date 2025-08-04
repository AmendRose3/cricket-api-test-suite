import pytest,requests,json
from utils.request_handler import send_get_request,make_graphql_request
from state import CountryState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
PROJECT_KEY ="RS_P_1912493998375911425"

BASE_URL="https://api.sports.roanuz.com/v5/cricket/{proj_key}/"
ENDPOINT = "association/list-by-country/{country_code}/"


def test_tc_01_valid_token_authentication(valid_headers_1):
    run_valid_token_authentication(ENDPOINT.format(country_code=CountryState.code), BASE_URL.format(proj_key= PROJECT_KEY), valid_headers_1)

def test_tc_02_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_tc_03_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_tc_04_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_05_structure_of_response(base_url, valid_headers_1):
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(country_code=CountryState.code)}"
    response = send_get_request(url, headers=valid_headers_1)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()

    # top level keys
    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing key: {key}"

    #associations structure
    assert isinstance(json_data["data"]["associations"], list), "associations should be a list"
    for assoc in json_data["data"]["associations"]:
        for field in ["key", "code", "name", "country", "parent"]:
            assert field in assoc, f"Missing field '{field}' in association"
        
        # country
        country = assoc["country"]
        expected_country_fields = ["short_code", "code", "name", "official_name", "is_region"]
        for field in expected_country_fields:
            assert field in country, f"Missing country field '{field}'"

    #cache
    cache = json_data["cache"]
    for field in ["key", "expires", "etag", "max_age"]:
        assert field in cache, f"Missing cache field '{field}'"



def test_tc_06_negative_page_number(valid_headers_1):
    PAGE = "-100/"
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(country_code=CountryState.code)}{PAGE}"
    res = send_get_request(url, headers=valid_headers_1)

    print(f"Status Code: {res.status_code}")
    print("Response Body:", res.text)

    assert res.status_code == 200, "Expected server to handle invalid page number gracefully (To recieve 200 code)"


def test_tc_07_zero_page_number(valid_headers_1):
    PAGE = "0/"
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(country_code=CountryState.code)}{PAGE}"
    res = send_get_request(url, headers=valid_headers_1)

    print(f"Status Code: {res.status_code}")
    print("Response Body:", res.text)

    assert res.status_code == 200, "Expected server to handle page=0 gracefully (To recieve 200 code)"


def test_tc_08_first_page_number(valid_headers_1):
    PAGE= "1/"
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(country_code=CountryState.code)}{PAGE}"
    res = send_get_request(url, headers=valid_headers_1)
    assert res.status_code == 200

    data = res.json()
    assert data is not None
    assert data["data"]["previous_page_key"] is None
    assert data["data"]["next_page_key"] is None

def test_tc_09_same_country_code(valid_headers_1):
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(country_code=CountryState.code)}"
    res = send_get_request(url, headers=valid_headers_1)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    data = res.json()
    associations = data["data"]["associations"]

    if associations:
        for assoc in associations:
            assert assoc["country"]["code"] == CountryState.code, (
                f"Expected country code {CountryState.code}")






