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


live_match_key="a-intern-test--cricket--Ca1949722003183411201"
completed_match_key='a-intern-test--cricket--yc1950078336558616577'
upcoming_key="a-intern-test--cricket--0Q1949781585960280066"
match_without_innings="a-intern-test--cricket--Mh1950826877283381252"

ENDPOINT = "match/{match_key}/run-rate/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(match_key=completed_match_key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_completed_match_manhattan_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=completed_match_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()["data"]

    assert data["first_bat_team"]["key"] == "a-intern-test--cricket--csk-a43S"
    assert isinstance(data["x"], list)
    assert isinstance(data["y"], list)
    assert isinstance(data["y2_wickets"], list)

def test_live_match_manhattan_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=live_match_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()["data"]

    assert data["first_bat_team"]["name"] == "Team A"
    assert isinstance(data["x"], list)
    assert isinstance(data["y"], list)
    assert isinstance(data["y2_wickets"], list)


def test_live_no_innings_match_manhattan_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=match_without_innings)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 500, f"Expected 500 error for match without innings, got {response.status_code}"

def test_upcoming_match_worm_graph_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=upcoming_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 400, f"Expected 400 error for upcoming match, got {response.status_code}"
    error = response.json()["error"]


def test_tc_04_rest_graphql_validate(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_POINTS_QUERY_FILE = "data/graph/run_rate_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["matchKey"] = live_match_key
    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_data = gql_response.json()["data"]["cricket_match_run_rate"]

    rest_url = f"{base_url}{ENDPOINT.format(match_key=live_match_key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_data = rest_response.json()["data"]


    assert gql_data["first_bat_team"]["key"] == rest_data["first_bat_team"]["key"], "Mismatch in first_bat_team key"
    assert gql_data["first_bat_team"]["code"] == rest_data["first_bat_team"]["code"], "Mismatch in first_bat_team code"
    assert gql_data["first_bat_team"]["name"] == rest_data["first_bat_team"]["name"], "Mismatch in first_bat_team name"

    assert gql_data["first_bowl_team"]["key"] == rest_data["first_bowl_team"]["key"], "Mismatch in first_bowl_team key"
    assert gql_data["first_bowl_team"]["code"] == rest_data["first_bowl_team"]["code"], "Mismatch in first_bowl_team code"
    assert gql_data["first_bowl_team"]["name"] == rest_data["first_bowl_team"]["name"], "Mismatch in first_bowl_team name"

    assert gql_data["x"] == rest_data["x"], "Mismatch in X-axis overs"
    assert gql_data["y"] == rest_data["y"], "Mismatch in Y-axis run rates"
    assert gql_data["y2_wickets"] == rest_data["y2_wickets"], "Mismatch in wickets data"
    assert gql_data["x_axis_label"] == rest_data["x_axis_label"], "Mismatch in X-axis label"
    assert gql_data["y_axis_label"] == rest_data["y_axis_label"], "Mismatch in Y-axis label"
    assert gql_data["data_label"] == rest_data["data_label"], "Mismatch in data labels"
    assert gql_data["y_colors"] == rest_data["y_colors"], "Mismatch in color codes"

    assert gql_data["chart_type"].lower() == rest_data["chart_type"].lower(), "Mismatch in chart type"
