import pytest, requests, json
from utils.request_handler import send_get_request, make_graphql_request
from tests.state import AssociationState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)

ENDPOINT = "featured-tournaments/"


def test_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)


def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)


def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)


def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_get_featured_tournaments_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"

    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data.get("http_status_code") == 200, "'http_status_code' is not 200"
    assert "data" in json_data, "'data' key missing in response"
    assert "tournaments" in json_data["data"], "'tournaments' key missing in data"

    tournaments = json_data["data"]["tournaments"]
    assert isinstance(tournaments, list), "'tournaments' should be a list"

    for tournament in tournaments:
        for field in [
            "key", "name", "short_name", "start_date", "gender",
            "point_system", "competition", "association_key", "sport",
            "is_date_confirmed", "is_venue_confirmed",
            "last_scheduled_match_date", "formats", "countries"
        ]:
            assert field in tournament, f"'{field}' missing in tournament"

        assert isinstance(tournament["competition"], dict), "'competition' should be a dict"
        for field in ["key", "code", "name"]:
            assert field in tournament["competition"], f"'{field}' missing in competition"

        assert isinstance(tournament["countries"], list), "'countries' should be a list"
        for country in tournament["countries"]:
            for field in ["short_code", "code", "name", "official_name", "is_region"]:
                assert field in country, f"'{field}' missing in country"

