import pytest, requests, json
from utils.request_handler import send_get_request, make_graphql_request
from utils.common import get_date_from_timestamp,get_todays_date,normalize_string
from tests.state import MatchState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
match="a-intern-test--cricket--yc1950078336558616577"
inning="B1"


ENDPOINT = "match/{match_key}/innings/{inning_key}/wagon-zone/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(match_key=match,inning_key=inning), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_response_structure_wagon_zone(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=match,inning_key=inning)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    response_json = response.json()
    assert "data" in response_json, "'data' key not in response"
    assert isinstance(response_json["data"], dict), "'data' should be a dictionary"

    wagon_zones = response_json["data"].get("wagon_zones")
    assert isinstance(wagon_zones, list), "'wagon_zones' should be a list"
    for wz in wagon_zones:
        assert "player" in wz, "'player' key missing in wagon zone entry"
        assert isinstance(wz["player"], str), "'player' should be a string"

        opponents = wz.get("opponents")
        assert isinstance(opponents, list), "'opponents' should be a list"

        for opponent in opponents:
            assert "player" in opponent, "'player' key missing in opponent"
            # 'player' can be None or str
            assert opponent["player"] is None or isinstance(opponent["player"], str), "'player' should be None or string"

            zones = opponent.get("zones")
            assert isinstance(zones, list), "'zones' should be a list"
            for zone in zones:
                assert "zone" in zone, "'zone' key missing in zone entry"
                assert "runs" in zone, "'runs' key missing in zone entry"
                assert isinstance(zone["zone"], str), "'zone' should be a string"
                assert isinstance(zone["runs"], int), "'runs' should be an integer"