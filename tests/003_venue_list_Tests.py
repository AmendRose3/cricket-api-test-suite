import pytest,requests,json
from utils.request_handler import send_get_request,make_graphql_request
from state import StadiumState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
page=1
ENDPOINT = "venue/list/{page}/"

def test_tc_01_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT.format(page=1), base_url, valid_headers)

def test_tc_02_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT.format(page=1), base_url, invalid_headers)

def test_tc_03_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT.format(page=1), base_url, no_token_headers)

def test_tc_04_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT.format(page=1), base_url, empty_token_headers)



def test_tc_05_get_venue_list_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(page=1)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_data = response.json()

    assert json_data.get("http_status_code") == 200, "'http_status_code' is not 200"
    assert "data" in json_data, "'data' key missing in response"
    assert "venues" in json_data["data"], "'venues' key missing in data"

    venues = json_data["data"]["venues"]
    assert isinstance(venues, list), "'venues' should be a list"

    for venue in venues:
        assert "key" in venue, "'key' missing in venue"
        assert "name" in venue, "'name' missing in venue"
        assert "city" in venue, "'city' missing in venue"
        assert "country" in venue, "'country' missing in venue"
        assert "geolocation" in venue, "'geolocation' missing in venue"

        country = venue["country"]
        assert isinstance(country, dict), "'country' should be a dict"
        assert "short_code" in country, "'short_code' missing in country"
        assert "code" in country, "'code' missing in country"
        assert "name" in country, "'name' missing in country"
        assert "official_name" in country, "'official_name' missing in country"
        assert "is_region" in country, "'is_region' missing in country"

def test_tc_06_graphql_rest_stadium_match_by_key(graphql_headers, valid_headers, base_url, graphql_url):
    GRAPHQL_PAYLOAD_FILE="data/association/stadium_search_query.json"
    with open(GRAPHQL_PAYLOAD_FILE, "r") as f:
        gql_payload = json.load(f)

    graphql_response = make_graphql_request(
        url=graphql_url,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert graphql_response.status_code == 200
    graphql_items = graphql_response.json()["data"]["sports_stadium_search"]["items"]

    rest_url = f"{base_url}{ENDPOINT.format(page=1)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200
    rest_items = rest_response.json()["data"]["venues"]

    target_key = StadiumState.key

    gql_obj = next((item for item in graphql_items if item["resource"]["hashkey"] == target_key), None)
    rest_obj = next((item for item in rest_items if item["key"] == target_key), None)

    assert gql_obj is not None, f"Key {target_key} not found in GraphQL response"
    assert rest_obj is not None, f"Key {target_key} not found in REST response"

    gql_stadium = gql_obj["stadium"]
    gql_locale = gql_obj["locale"]

    assert gql_stadium["name"] == rest_obj["name"]
    assert gql_locale["geo_location"] == rest_obj["geolocation"]



def test_tc_07_negative_page_number(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT.format(page=-100)}"
    res = send_get_request(url, headers=valid_headers)

    print("Response status code:", res.status_code)
    print("Response body:", res.text)

    assert res.status_code == 404, "Expected 404 Not Found for negative page number"



def test_tc_08_zero_page_number(valid_headers, base_url):

    url = f"{base_url}{ENDPOINT.format(page=0)}"
    res = send_get_request(url, headers=valid_headers)

    assert res.status_code == 500, "Expected server to handle page=0 gracefully, but got 500."


def test_tc_09_first_page_number(valid_headers, base_url):

    url = f"{base_url}{ENDPOINT.format(page= 1)}"
    res = send_get_request(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    assert data is not None
    assert data["data"]["previous_page_key"] is None
    assert data["data"]["next_page_key"] is None

def test_tc_10_beyond_page_number(valid_headers, base_url):

    url = f"{base_url}{ENDPOINT.format(page= 100)}"
    res = send_get_request(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    assert data is not None
    assert len(data["data"]["venues"]) == 0
    assert data["data"]["previous_page_key"] == 99
    assert data["data"]["next_page_key"] is None


