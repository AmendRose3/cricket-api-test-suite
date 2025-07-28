import pytest,requests,json
from utils.request_handler import send_get_request,make_graphql_request
from state import CountryState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
ENDPOINT = "country/list/"

def test_tc_01_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_tc_02_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_tc_03_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_tc_04_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_get_country_list_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_data = response.json()

    assert json_data["http_status_code"] == 200, "Invalid 'http_status_code'"
    assert "data" in json_data and "countries" in json_data["data"], "'countries' not found in 'data'"
    countries = json_data["data"]["countries"]
    assert isinstance(countries, list), "'countries' should be a list"

    for country in countries:
        assert "name" in country, "'name' missing in country"
        assert "code" in country, "'code' missing in country"
        assert "short_code" in country, "'short_code' missing in country"
        assert "official_name" in country, "'official_name' missing in country"
        assert "is_region" in country, "'is_region' missing in country"


def test_tc_06_filter_associations_by_country(valid_headers, base_url):
    country_code = CountryState.code
    country_url = f"{base_url}{ENDPOINT}"
    association_url = f"{base_url}association/list/"

    country_response = send_get_request(country_url, headers=valid_headers)
    assert country_response.status_code == 200
    country_data = country_response.json()
    countries = country_data["data"]["countries"]

    code_country = next((c for c in countries if c["code"] == country_code), None)
    assert code_country is not None, "country code  not found in country list"

    association_response = send_get_request(association_url, headers=valid_headers)
    assert association_response.status_code == 200
    association_data = association_response.json()
    associations = association_data["data"]["associations"]

    aus_associations = [
        assoc for assoc in associations
        if assoc.get("country", {}).get("code") == country_code
    ]

    assert aus_associations, "No associations found for the country code"
    
def test_tc_07_validate_india_official_name(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200

    countries = response.json()["data"]["countries"]

    india = next((c for c in countries if c["code"] == "IND"), None)
    assert india is not None, "India not found in country list"

    assert india["name"] == "India"
    assert india["official_name"] == "Republic of India"

def test_tc_08_validate_canada_official_name(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200

    countries = response.json()["data"]["countries"]

    canada = next((c for c in countries if c["code"] == "CAN"), None)
    assert canada is not None, "Canada not found in country list"

    assert canada["name"] == "Canada"
    assert canada["official_name"] == "Canada"




def test_tc_09_negative_page_number(valid_headers, base_url):
    PAGE = "-100/"
    url = f"{base_url}{ENDPOINT}{PAGE}"
    res = send_get_request(url, headers=valid_headers)

    # print(f"Status Code: {res.status_code}")
    # print("Response Body:", res.text)

    assert res.status_code == 500, "Expected server to handle invalid page number gracefully, but got 500."


def test_tc_10_zero_page_number(valid_headers, base_url):
    PAGE = "0/"
    url = f"{base_url}{ENDPOINT}{PAGE}"
    res = send_get_request(url, headers=valid_headers)

    # print(f"Status Code: {res.status_code}")
    # print("Response Body:", res.text)

    assert res.status_code == 500, "Expected server to handle page=0 gracefully, but got 500."


def test_tc_11_first_page_number(valid_headers, base_url):
    PAGE= "1/"
    url = f"{base_url}{ENDPOINT}{PAGE}"
    res = send_get_request(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    assert data is not None
    assert data["data"]["previous_page_key"] is None
    assert data["data"]["next_page_key"] is None



def test_tc_12_graphql_rest_country_match(graphql_headers, valid_headers,base_url,graphql_url):

    GRAPHQL_ENDPOINT = f"{graphql_url}"
    REST_COUNTRY_ENDPOINT = f"{base_url}{ENDPOINT}"
    GRAPHQL_PAYLOAD_FILE = "data/association/region_read_query.json"

    with open(GRAPHQL_PAYLOAD_FILE, "r") as f:
        gql_payload = json.load(f)

    graphql_response = make_graphql_request(
        url=GRAPHQL_ENDPOINT,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert graphql_response.status_code == 200

    graphql_data = graphql_response.json()["data"]["sports_region_read"]["item"]["region"]
    code_country = graphql_data["code"]

    rest_response = send_get_request(REST_COUNTRY_ENDPOINT, headers=valid_headers)
    assert rest_response.status_code == 200

    countries = rest_response.json()["data"]["countries"]
    matched_country = next((c for c in countries if c["code"] == code_country), None)
    assert matched_country is not None, f"Country with code {code_country} not found in REST response"

    assert graphql_data["short_code"] == matched_country["short_code"]
    assert graphql_data["code"] == matched_country["code"]
    assert graphql_data["name"] == matched_country["name"]
    assert graphql_data["official_name"] == matched_country["official_name"]