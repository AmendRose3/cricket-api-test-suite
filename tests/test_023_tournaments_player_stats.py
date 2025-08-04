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
ENDPOINT = "tournament/{tournament_key}/player/{player_key}/stats/"
PROJECT_KEY ="RS_P_1912493998375911425"

Tournament="a-rz--cricket--icc--icccwclt--2023-27-8JlY"
Player="c__player__aryansh_sharma__a275c"


def test_valid_token_authentication(valid_headers_1):
    print(valid_headers_1)
    run_valid_token_authentication(ENDPOINT.format(tournament_key=Tournament,player_key=Player), BASE_URL.format(proj_key= PROJECT_KEY), valid_headers_1)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT.format(tournament_key=Tournament,player_key=Player), base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT.format(tournament_key=Tournament,player_key=Player), base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT.format(tournament_key=Tournament,player_key=Player), base_url, empty_token_headers)


def test_tc_01_stats_structure(valid_headers_1):
    url = f"{BASE_URL.format(proj_key=PROJECT_KEY)}{ENDPOINT.format(tournament_key=Tournament, player_key=Player)}"
    response = send_get_request(url, headers=valid_headers_1)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    json_data = response.json()
    assert "data" in json_data, "'data' key missing in response"
    data = json_data["data"]

    assert "stats" in data, "'stats' section missing in data"
    assert "data_review" in data, "'data_review' section missing in data"

    stats = data["stats"]

    for category in ["batting", "bowling", "fielding"]:
        assert category in stats, f"'{category}' missing in stats"
        assert isinstance(stats[category], dict), f"'{category}' should be a dict"

    assert "player" in stats, "'player' details missing in stats"
    player_info = stats["player"]
    for field in ["key", "name", "gender", "nationality", "date_of_birth", "seasonal_role"]:
        assert field in player_info, f"'{field}' missing in player info"

    batting = stats["batting"]
    expected_batting_keys = [
        "matches", "innings", "not_outs", "runs", "balls", "fours", "sixes",
        "average", "strike_rate", "fifties", "hundreds", "double_hundreds",
        "high_score", "high_score_str", "thirties", "best"
    ]
    for key in expected_batting_keys:
        assert key in batting, f"'{key}' missing in batting stats"

    assert isinstance(batting["best"], dict), "'best' in batting should be a dict"
    for field in ["runs", "balls", "fours", "sixes", "strike_rate", "team_against", "match_key"]:
        assert field in batting["best"], f"'{field}' missing in batting.best"
