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

ENDPOINT = "tournament/{tournament_key}/featured-matches-2/"



def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(tournament_key=TournamentState.key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)


def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)


def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_get_featured_matches_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_data = response.json()

    assert json_data.get("http_status_code") == 200, "'http_status_code' is not 200"
    assert "data" in json_data, "'data' key missing in response"
    assert "matches" in json_data["data"], "'matches' key missing in data"

    matches = json_data["data"]["matches"]
    assert isinstance(matches, list), "'matches' should be a list"

    for match in matches:
        assert "key" in match, "'key' missing in match"
        assert "name" in match, "'name' missing in match"
        assert "short_name" in match, "'short_name' missing in match"
        assert "sub_title" in match, "'sub_title' missing in match"
        assert "status" in match, "'status' missing in match"
        assert "start_at" in match, "'start_at' missing in match"
        assert "tournament" in match, "'tournament' missing in match"
        assert "metric_group" in match, "'metric_group' missing in match"
        assert "sport" in match, "'sport' missing in match"
        assert "teams" in match, "'teams' missing in match"
        assert "venue" in match, "'venue' missing in match"
        assert "association" in match, "'association' missing in match"
        assert "format" in match, "'format' missing in match"

        # Tournament details
        tournament = match["tournament"]
        assert isinstance(tournament, dict), "'tournament' should be a dict"
        for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
            assert field in tournament, f"'{field}' missing in tournament"

        # Teams structure
        teams = match["teams"]
        for side in ["a", "b"]:
            assert side in teams, f"'{side}' team missing in match"
            team = teams[side]
            for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name", "country_code"]:
                assert field in team, f"'{field}' missing in team {side}"

        # Venue check
        venue = match["venue"]
        for field in ["key", "name", "city", "country"]:
            assert field in venue, f"'{field}' missing in venue"
        country = venue["country"]
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert field in country, f"'{field}' missing in venue country"

        # Association
        association = match["association"]
        for field in ["key", "code", "name"]:
            assert field in association, f"'{field}' missing in association"
    


def test_tc_06_featured_matches_live_match(base_url, valid_headers):

    MATCH_ID = "a-intern-test--cricket--Ca1949722003183411201"

    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200
    data = response.json().get("data", {})
    matches = data.get("matches", [])

    match = next((m for m in matches if m["key"] == MATCH_ID), None)

    assert match is not None, f"Match with ID {MATCH_ID} not found"
    assert match["winner"] is not None
    assert match["status"] == "started", f"Expected 'started', got '{match['status']}'"
    match_start_date = get_date_from_timestamp(match["start_at"])
    today = get_todays_date()

    assert match_start_date == today, f"Match date {match_start_date} is not today {today}"

def test_tc_07_featured_matches_not_started_match(base_url, valid_headers):

    MATCH_ID = "a-intern-test--cricket--0u1949728595337461761"

    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200
    data = response.json().get("data", {})
    matches = data.get("matches", [])

    match = next((m for m in matches if m["key"] == MATCH_ID), None)

    assert match is not None, f"Match with ID {MATCH_ID} not found"
    assert match["winner"] is None
    assert match["status"] == "not_started", f"Expected 'started', got '{match['status']}'"
    match_start_date = get_date_from_timestamp(match["start_at"])
    today = get_todays_date()

    assert match_start_date > today, f"Match date {match_start_date} is not today {today}"


def test_tc_08_featured_matches_completed_match(base_url, valid_headers):

    MATCH_ID = "a-intern-test--cricket--Xa1949742259796885506"

    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200
    data = response.json().get("data", {})
    matches = data.get("matches", [])

    match = next((m for m in matches if m["key"] == MATCH_ID), None)

    assert match is not None, f"Match with ID {MATCH_ID} not found"
    assert match["winner"] is not None
    assert match["status"] == "completed", f"Expected 'started', got '{match['status']}'"
    match_start_date = get_date_from_timestamp(match["start_at"])
    today = get_todays_date()

    assert match_start_date < today, f"Match date {match_start_date} is not today {today}"


def test_tc_09_graphql_rest_featured_matches_match(graphql_headers, valid_headers, base_url):
    graphql_url = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_PAYLOAD_FILE = "data/tournament/featured_matches_query.json"

    with open(GRAPHQL_PAYLOAD_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key

    graphql_response = make_graphql_request(
        url=graphql_url,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )


    assert graphql_response.status_code == 200, f"GraphQL error: {graphql_response.text}"

    gql_matches = graphql_response.json()["data"]["cricket_tournament_featured_matches"]["matches"]
    assert isinstance(gql_matches, list) and len(gql_matches) > 0, "No matches in GraphQL response"

    gql_dict = {match["key"]: match for match in gql_matches}

    rest_url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"    
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST failed: {rest_response.text}"
    rest_matches = rest_response.json()["data"]["matches"]
    assert isinstance(rest_matches, list) and len(rest_matches) > 0, "No matches in REST response"

    rest_dict = {match["key"]: match for match in rest_matches}

    for match_key, gql_match in gql_dict.items():

        assert match_key in rest_dict, f"Match key {match_key} missing in REST response"
        rest_match = rest_dict[match_key]
        gql_status = gql_match["status"]
        rest_status = rest_match["status"]
        gql_status = normalize_string(gql_match["status"])
        rest_status = normalize_string(rest_match["status"])
        assert gql_status == rest_status, f"Status mismatch for {match_key}: GQL={gql_status}, REST={rest_status}"
        gql_winner = normalize_string(gql_match["winner"])
        rest_winner = normalize_string(rest_match["winner"])
        assert gql_winner == rest_winner, f"Winner mismatch for {match_key}: GQL={gql_winner}, REST={rest_winner}"
        assert gql_match["start_at"] == rest_match["start_at"], f"Start time mismatch for {match_key}"


