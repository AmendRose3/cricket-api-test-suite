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

ENDPOINT = "tournament/{tournament_key}/fixtures/"



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



def test_tc_05_get_tournament_fixtures_valid(base_url, valid_headers):
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
        for field in ["key", "name", "short_name", "sub_title", "status", "start_at", "tournament",
                      "metric_group", "sport", "teams", "venue", "association", "format", "gender"]:
            assert field in match, f"'{field}' missing in match"

        # tournament details
        tournament = match["tournament"]
        assert isinstance(tournament, dict), "'tournament' should be a dict"
        for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
            assert field in tournament, f"'{field}' missing in tournament"

        # team structure
        teams = match["teams"]
        for side in ["a", "b"]:
            assert side in teams, f"'{side}' team missing"
            team = teams[side]
            for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name", "country_code"]:
                assert field in team, f"'{field}' missing in team {side}"

        # venue structure
        venue = match["venue"]
        for field in ["key", "name", "city", "country"]:
            assert field in venue, f"'{field}' missing in venue"

        country = venue["country"]
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert field in country, f"'{field}' missing in venue.country"

        # association
        association = match["association"]
        for field in ["key", "code", "name"]:
            assert field in association, f"'{field}' missing in association"

        status = normalize_string(match["status"])
        assert status in ["completed", "started", "notstarted"], f"Invalid status: {match['status']}"


# Undecided Venues
# "venue": {
#                     "key": "a-intern-test--tbc2-iUH8",
#                     "name": "TBD",
#                     "city": "TBD",
#                     "country": {
#                         "short_code": null,
#                         "code": null,
#                         "name": null,
#                         "official_name": null,
#                         "is_region": false
#                     },
#                     "geolocation": null
#                 }

import pytest
import requests

def test_tc_06_check_tbd_venue_from_fixtures(base_url, valid_headers):
    match_key = "a-intern-test--cricket--0Q1949781585960280066"
    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    
    response = requests.get(url, headers=valid_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    matches = response.json().get("data", {}).get("matches", [])
    assert matches, "No matches found in fixture list"

    match = next((m for m in matches if m.get("key") == match_key), None)
    assert match is not None, f"Match with key {match_key} not found"

    venue = match.get("venue", {})
    assert venue, "Venue data missing"

    assert venue.get("name", "").strip().lower() == "tbd", "Venue name is not 'TBD'"
    assert venue.get("city", "").strip().lower() == "tbd", "Venue city is not 'TBD'"

    country = venue.get("country", {})
    assert country.get("short_code") is None
    assert country.get("code") is None
    assert country.get("name") is None
    assert country.get("official_name") is None
    assert country.get("is_region") is False
    assert venue.get("geolocation") is None, "Venue geolocation should be None"


def test_tc_07_rest_match_graphql(valid_headers, graphql_headers, base_url):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_FIXTURE_QUERY_FILE = "data/tournament/tournament_fixtures_query.json"
    # Load GraphQL fixture payload
    with open(GRAPHQL_FIXTURE_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key

    # GraphQL
    graphql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )

    assert graphql_response.status_code == 200, f"GraphQL error: {graphql_response.text}"
    gql_matches = graphql_response.json()["data"]["cricket_tournament_fixtures"]["matches"]
    assert isinstance(gql_matches, list) and gql_matches, "No matches in GraphQL response"

    gql_dict = {match["key"]: match for match in gql_matches}

    # REST
    rest_url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST error: {rest_response.text}"
    rest_matches = rest_response.json()["data"]["matches"]
    assert isinstance(rest_matches, list) and rest_matches, "No matches in REST response"

    rest_dict = {match["key"]: match for match in rest_matches}

    for match_key, rest_match in rest_dict.items():
        assert match_key in gql_dict, f"Match key {match_key} present in REST but missing in GraphQL"

        gql_match = gql_dict[match_key]

        gql_status = normalize_string(gql_match["status"])
        rest_status = normalize_string(rest_match["status"])
        assert gql_status == rest_status, f"Status mismatch for {match_key}: GQL={gql_status}, REST={rest_status}"

        gql_winner = normalize_string(gql_match["winner"])
        rest_winner = normalize_string(rest_match["winner"])
        assert gql_winner == rest_winner, f"Winner mismatch for {match_key}: GQL={gql_winner}, REST={rest_winner}"

        assert gql_match["start_at"] == rest_match["start_at"], f"Start time mismatch for {match_key}"

