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

ENDPOINT = "match/{match_key}/worm/"

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

def test_completed_match_worm_graph_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=completed_match_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()

    data = json_data["data"]
    assert data is not None, "Expected data in response"
    assert "first_bat_team" in data and "first_bowl_team" in data, "Missing team info"
    assert isinstance(data["x"], list), "Expected x to be a list"
    assert isinstance(data["y"], list) and isinstance(data["y2_wickets"], list), "Expected y and y2_wickets to be lists"
    assert data["chart_type"] == "line", "Unexpected chart type"


def test_live_match_worm_graph_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=live_match_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data is not None, "Expected data in response"
    assert isinstance(data["y"], list) and isinstance(data["y2_wickets"], list), "Expected y and y2_wickets to be lists"
    assert len(data["y"]) == 2, "Expected 2 innings data (even if one is empty)"


def test_live_no_innings_match_worm_graph_response(base_url, valid_headers):

    url = f"{base_url}{ENDPOINT.format(match_key=match_without_innings)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    assert "Server got itself in trouble" in response.text or "Internal Server Error" in response.text


def test_upcoming_match_worm_graph_response(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=upcoming_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    json_data = response.json()

    assert json_data["data"] is None, "Expected data to be null"
    assert json_data["error"]["code"] == "A-400-0", f"Unexpected error code: {json_data['error']['code']}"
    assert json_data["error"]["msg"] == "Invalid input to process", f"Unexpected error message: {json_data['error']['msg']}"


def test_tc_04_rest_graphql_validate(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_POINTS_QUERY_FILE = "data/graph/worm_query.json"

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
    gql_match = gql_response.json()["data"]["cricket_match_worm"]

    rest_url = f"{base_url}{ENDPOINT.format(match_key=live_match_key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_match = rest_response.json()["data"]

    # first_bat_team
    gql_bat = gql_match["first_bat_team"]
    rest_bat = rest_match["first_bat_team"]
    assert gql_bat["key"] == rest_bat["key"], "Mismatch in first_bat_team key"
    assert gql_bat["code"] == rest_bat["code"], "Mismatch in first_bat_team code"
    assert gql_bat["name"] == rest_bat["name"], "Mismatch in first_bat_team name"

    # first_bowl_team
    gql_bowl = gql_match["first_bowl_team"]
    rest_bowl = rest_match["first_bowl_team"]
    assert gql_bowl["key"] == rest_bowl["key"], "Mismatch in first_bowl_team key"
    assert gql_bowl["code"] == rest_bowl["code"], "Mismatch in first_bowl_team code"
    assert gql_bowl["name"] == rest_bowl["name"], "Mismatch in first_bowl_team name"

    # graph values
    assert gql_match["x"] == rest_match["x"], "Mismatch in x (overs) values"
    assert gql_match["y"] == rest_match["y"], "Mismatch in y (runs) values"
    assert gql_match["y2_wickets"] == rest_match["y2_wickets"], "Mismatch in y2_wickets values"
    assert gql_match["x_axis_label"] == rest_match["x_axis_label"], "Mismatch in x_axis_label"
    assert gql_match["y_axis_label"] == rest_match["y_axis_label"], "Mismatch in y_axis_label"
    assert gql_match["data_label"] == rest_match["data_label"], "Mismatch in data_label"
    
    assert gql_match["chart_type"].lower() == rest_match["chart_type"].lower(), "Mismatch in chart_type"

    assert gql_match["y_colors"] == rest_match["y_colors"], "Mismatch in y_colors"
