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
COMPLETED_MATCH="a-intern-test--cricket--KU1950455781946204164"
LIVE_MATCH="a-intern-test--cricket--Ca1949722003183411201"
UPCOMING_MATCH="a-intern-test--cricket--qT1950798302987603974"
UPCOMING_MATCH_AFTER_10_DAYS="a-intern-test--cricket--0Q1949781585960280066"


ENDPOINT = "match/{match_key}/pre-match-odds/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    run_valid_token_authentication(ENDPOINT.format(match_key=UPCOMING_MATCH), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_01_completed_match_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=COMPLETED_MATCH)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 404, f"Unexpected status code: {response.status_code}"
    
    json_data = response.json()
    assert json_data["data"] is None
    assert json_data["error"]["code"] == "DNA-404-1"
    assert "match completed" in json_data["error"]["msg"].lower()

def test_tc_02_live_match_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=LIVE_MATCH)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 404, f"Unexpected status code: {response.status_code}"

    json_data = response.json()
    assert json_data["data"] is None
    assert json_data["error"]["code"] == "DNA-404-5"
    assert "match has started" in json_data["error"]["msg"].lower()

# match in 10 days
def test_tc_03_upcoming_match_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=UPCOMING_MATCH)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    json_data = response.json()
    match_data = json_data["data"]["match"]

    decimal_odds = match_data["bet_odds"]["automatic"]["decimal"]
    assert isinstance(decimal_odds, list) and len(decimal_odds) == 2
    for team in decimal_odds:
        assert "team_key" in team and "value" in team

    fractional_odds = match_data["bet_odds"]["automatic"]["fractional"]
    for team in fractional_odds:
        assert "numerator" in team
        assert "denominator" in team
        assert isinstance(team["numerator"], int)
        assert isinstance(team["denominator"], int)

    result_prediction = match_data["result_prediction"]["automatic"]["percentage"]
    assert isinstance(result_prediction, list) and len(result_prediction) == 2
    for prediction in result_prediction:
        assert "team_key" in prediction
        assert "value" in prediction
        assert isinstance(prediction["value"], float)

    teams = match_data["teams"]
    assert isinstance(teams, dict) and len(teams) == 2
    for team_key, team in teams.items():
        assert all(k in team for k in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name"])

    meta = match_data["meta"]
    assert meta["status"] == "not_started"
    assert meta["format"] == "t10"
    assert isinstance(meta["start_at"], float)

# Match that starts after 10 days
def test_tc_05_invalid_input_after_10_days(base_url, valid_headers):

    url = f"{base_url}{ENDPOINT.format(match_key=UPCOMING_MATCH_AFTER_10_DAYS)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    json_data = response.json()
    assert json_data["error"]["code"] == "A-400-0", f"Unexpected error code: {json_data['error']['code']}"
    assert json_data["error"]["msg"] == "Invalid input to process", f"Unexpected message: {json_data['error']['msg']}"
    assert json_data["error"]["http_status_code"] == 400, "Incorrect http_status_code in error block"

def test_tc_04_rest_graphql_validate(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_POINTS_QUERY_FILE = "data/match_odds/pre_match_odds_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["matchKey"] = UPCOMING_MATCH

    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_match = gql_response.json()["data"]["cricket_match_pre_match_odds"]["match"]

    rest_url = f"{base_url}{ENDPOINT.format(match_key=UPCOMING_MATCH)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_match = rest_response.json()["data"]["match"]

    # DECIMAL odds
    gql_decimal = {item["team_key"]: item["value"] for item in gql_match["bet_odds"]["automatic"]["decimal"]}
    rest_decimal = {item["team_key"]: item["value"] for item in rest_match["bet_odds"]["automatic"]["decimal"]}
    assert gql_decimal == rest_decimal, f"Mismatch in decimal odds"

    #FRACTIONAL odds
    gql_fractional = {
        item["team_key"]: {
            "value": item["value"],
            "numerator": item["numerator"],
            "denominator": item["denominator"]
        } for item in gql_match["bet_odds"]["automatic"]["fractional"]
    }
    rest_fractional = {
        item["team_key"]: {
            "value": item["value"],
            "numerator": item["numerator"],
            "denominator": item["denominator"]
        } for item in rest_match["bet_odds"]["automatic"]["fractional"]
    }
    assert gql_fractional == rest_fractional, f"Mismatch in fractional odds: {gql_fractional} vs {rest_fractional}"

    #RESULT PREDICTION percentages
    gql_percentages = {item["team_key"]: item["value"] for item in gql_match["result_prediction"]["automatic"]["percentage"]}
    rest_percentages = {item["team_key"]: item["value"] for item in rest_match["result_prediction"]["automatic"]["percentage"]}
    assert gql_percentages == rest_percentages, f"Mismatch in result prediction: {gql_percentages} vs {rest_percentages}"


