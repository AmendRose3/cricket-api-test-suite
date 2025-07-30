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

ENDPOINT = "featured-matches-2/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_05_featured_matches_detail_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()

    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    matches = json_data["data"].get("matches")
    assert isinstance(matches, list), "'matches' should be a list"

    for match in matches:
        for field in [
            "key", "name", "short_name", "sub_title", "status", "start_at",
            "tournament", "sport", "winner", "teams", "venue", "association",
            "gender", "format", "estimated_end_date", "completed_date_approximate"
        ]:
            assert field in match, f"Missing field in match: {field}"

        # Tournament details
        tournament = match["tournament"]
        assert isinstance(tournament, dict), "'tournament' should be a dict"
        for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
            assert field in tournament, f"Missing field in tournament: {field}"

        # Teams
        teams = match["teams"]
        assert isinstance(teams, dict), "'teams' should be a dict"
        for team_key in ["a", "b"]:
            assert team_key in teams, f"Missing team key: {team_key}"
            team = teams[team_key]
            for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name", "country_code"]:
                assert field in team, f"Missing field in team '{team_key}': {field}"

        # Venue
        venue = match["venue"]
        assert isinstance(venue, dict), "'venue' should be a dict"
        for field in ["key", "name", "city", "country"]:
            assert field in venue, f"Missing field in venue: {field}"
        country = venue["country"]
        assert isinstance(country, dict), "'country' in venue should be a dict"
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert field in country, f"Missing field in venue country: {field}"

        # Association
        association = match["association"]
        assert isinstance(association, dict), "'association' should be a dict"
        for field in ["key", "code", "name"]:
            assert field in association, f"Missing field in association: {field}"

    intelligent_order = json_data["data"].get("intelligent_order")
    assert isinstance(intelligent_order, list), "'intelligent_order' should be a list"

    cache = json_data["cache"]
    for field in ["key", "expires", "etag", "max_age"]:
        assert field in cache, f"Missing field in cache: {field}"

    assert json_data["http_status_code"] == 200, "'http_status_code' should be 200"

def test_tc_06_match_featured_rest_vs_graphql(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_POINTS_QUERY_FILE = "data/match/featured_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)


    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_matches = gql_response.json()["data"]["cricket_featured_matches"]["matches"]
    gql_match_map = {match["key"]: match for match in gql_matches}

    rest_url =f"{base_url}{ENDPOINT}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_matches = rest_response.json()["data"]["matches"]

    for rest_match in rest_matches:
        key = rest_match["key"]
        assert key in gql_match_map, f"Match key '{key}' not found in GraphQL response"
        gql_match = gql_match_map[key]

        for field in ["status", "start_at", "winner"]:
            rest_val = normalize_string(rest_match.get(field))
            gql_val = normalize_string(gql_match.get(field))
            assert rest_val == gql_val, f"Mismatch in '{field}' for key '{key}': REST={rest_val}, GQL={gql_val}"





