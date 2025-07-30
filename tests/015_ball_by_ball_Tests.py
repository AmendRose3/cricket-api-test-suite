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

OVER_KEY='b_1_2'
ENDPOINT = "match/{match_key}/ball-by-ball/"
FIRST_OVER_ENDPOINT = "match/{match_key}/ball-by-ball/FIRST-OVER/"
OVER_KEY_ENDPOINT = "match/{match_key}/ball-by-ball/FIRST-OVER/{over_key}/"


def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(match_key=MatchState.key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_06_ball_by_ball_over_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()

    # Top-level keys
    for field in ["data", "cache", "schema", "error", "http_status_code"]:
        assert field in json_data, f"Missing top-level field: {field}"

    # Data section
    data = json_data["data"]
    required_data_fields = ["over", "previous_over_index", "next_over_index", "previous_over_key", "next_over_key"]
    for field in required_data_fields:
        assert field in data, f"Missing field in 'data': {field}"

    # Over -> index
    over = data["over"]
    assert "index" in over, "Missing 'index' in over"
    assert "innings" in over["index"], "Missing innings in over index"
    assert "over_number" in over["index"], "Missing over_number in over index"

    # Over -> balls
    assert "balls" in over, "Missing 'balls' in over"
    balls = over["balls"]
    assert isinstance(balls, list), "Balls should be a list"
    for ball in balls:
        required_ball_fields = [
            "key", "ball_type", "batting_team", "comment", "innings", "overs", "batsman",
            "bowler", "team_score", "fielders", "non_striker_key", "entry_time",
            "ball_play_status", "ball_tags", "updated_time", "repr"
        ]
        for field in required_ball_fields:
            assert field in ball, f"Missing ball field: {field}"

        # batsman structure
        batsman_fields = ["player_key", "ball_count", "runs", "is_dot_ball", "is_four", "is_six"]
        for field in batsman_fields:
            assert field in ball["batsman"], f"Missing batsman field: {field}"

        # bowler structure
        bowler_fields = ["player_key", "ball_count", "runs", "extras", "is_wicket"]
        for field in bowler_fields:
            assert field in ball["bowler"], f"Missing bowler field: {field}"

        # team_score structure
        score_fields = ["ball_count", "runs", "extras", "is_wicket"]
        for field in score_fields:
            assert field in ball["team_score"], f"Missing team_score field: {field}"

        # Optional wicket info
        if ball.get("team_score", {}).get("is_wicket"):
            assert "wicket" in ball, "Missing 'wicket' info for wicket ball"
            wicket_fields = ["player_key", "wicket_type"]
            for field in wicket_fields:
                assert field in ball["wicket"], f"Missing wicket field: {field}"

    # previous_over_index
    if data["previous_over_index"]:
        assert "innings" in data["previous_over_index"]
        assert "over_number" in data["previous_over_index"]

    # cache structure
    cache = json_data["cache"]
    for field in ["key", "expires", "etag", "max_age"]:
        assert field in cache, f"Missing cache field: {field}"

    # schema versioning
    schema = json_data["schema"]
    assert schema["major_version"] == "5.0", "Unexpected schema major version"
    assert "minor_version" in schema

    # status code
    assert json_data["http_status_code"] == 200, "Invalid HTTP status"


def test_tc_07_validate_first_over(base_url, valid_headers):
    url = f"{base_url}{FIRST_OVER_ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    json_data = response.json()
    data = json_data["data"]
    over_index = data["over"]["index"]
    assert over_index["over_number"] == 1, f"Expected innings number 1"

    balls = data["over"]["balls"]
    assert len(balls) == 2, f"Expected 6 balls in the over, but got {len(balls)}"

def test_tc_08_validate__over_key_result(base_url, valid_headers):

    url = f"{base_url}{FIRST_OVER_ENDPOINT.format(match_key=MatchState.key,over_key=OVER_KEY)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"


    json_data = response.json()
    data = json_data["data"]

    innings = data["over"]["index"]["innings"]
    assert innings == "b_1", f"Expected innings 'b_1', got '{innings}'"

    over_number = data["over"]["index"]["over_number"]
    assert over_number == 2, f"Expected over number 2, got {over_number}"









 