import pytest, requests, json
from utils.request_handler import send_get_request, make_graphql_request
from utils.common import get_date_from_timestamp,get_todays_date,normalize_string
from tests.state import TournamentState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
BASE_URL="https://api.sports.roanuz.com/v5/cricket/{proj_key}/"
ENDPOINT = "tournament/{tournament_key}/stats/"
PROJECT_KEY ="RS_P_1912493998375911425"

Tournament="a-rz--cricket--icc--icccwclt--2023-27-8JlY"

def test_valid_token_authentication(valid_headers_1):
    print(valid_headers_1)
    run_valid_token_authentication(ENDPOINT.format(tournament_key=Tournament), BASE_URL.format(proj_key= PROJECT_KEY), valid_headers_1)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT.format(tournament_key=Tournament), base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT.format(tournament_key=Tournament), base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT.format(tournament_key=Tournament), base_url, empty_token_headers)

def test_tc_01_stats_structure(valid_headers_1):
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(tournament_key=Tournament)}"
    response = send_get_request(url, headers=valid_headers_1)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    
    json_data = response.json()
    assert "data" in json_data, "'data' key missing in response"
    data = json_data["data"]

    expected_data_sections = ["player", "team", "counter", "players", "teams", "data_review"]
    for section in expected_data_sections:
        assert section in data, f"'{section}' section missing in data"

    assert "batting" in data["player"], "'batting' section missing under 'player'"
    assert "bowling" in data["player"], "'bowling' section missing under 'player'"
    assert "fielding" in data["player"], "'fielding' section missing under 'player'"
    for category in ["batting", "bowling", "fielding"]:
        section = data["player"][category]
        assert isinstance(section, dict), f"'{category}' section should be a dict"

    assert "counter" in data, "'counter' section missing in data"
    counter = data["counter"]
    expected_counter_keys = [
        "runs", "fours", "sixes", "wickets", "completed_matches", "pending_matches"
    ]
    for key in expected_counter_keys:
        assert key in counter, f"'{key}' missing in 'counter'"
        assert isinstance(counter[key], int), f"'{key}' in 'counter' should be an integer"
