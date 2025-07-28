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

ENDPOINT = "tournament/{tournament_key}/"



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


def test_tc_05_tournament_detail_structure(base_url, valid_headers):

    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    response = send_get_request(url, headers=valid_headers)
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    
    json_data = response.json()

    # Top-level keys
    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    # Tournament
    tournament = json_data["data"].get("tournament")
    assert isinstance(tournament, dict), "'tournament' should be a dict"
    assert "key" in tournament
    assert "name" in tournament
    assert "start_date" in tournament
    assert isinstance(tournament.get("countries"), list)

    #country 
    for country in tournament["countries"]:
        assert isinstance(country, dict)
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert field in country

    #Teams
    teams = json_data["data"].get("teams")
    assert isinstance(teams, dict), "'teams' should be a dict"
    for team_key, team_info in teams.items():
        assert isinstance(team_info, dict)
        for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name"]:
            assert field in team_info

    # Rounds
    rounds = json_data["data"].get("rounds")
    assert isinstance(rounds, list), "'rounds' should be a list"
    for rnd in rounds:
        assert "key" in rnd
        assert "name" in rnd
        assert "groups" in rnd
        assert isinstance(rnd["groups"], list)
        for group in rnd["groups"]:
            assert "key" in group
            assert "name" in group
            assert isinstance(group.get("team_keys"), list)
            assert isinstance(group.get("match_keys"), list)


# tournament is bilateral (exactly 2 unique teams)
#wrong
# def test_tc_06_tournament_is_bilateral(base_url, valid_headers):

#     key="a-intern-test--cricket--bcci-OFJF--tour-ta-6K43-tb-W9Df-T20--2025-i3Xi"

#     url = f"{base_url}{ENDPOINT.format(tournament_key=key)}"
#     response = send_get_request(url, headers=valid_headers)
    
#     assert response.status_code == 200, "Invalid response"
#     json_data = response.json()

#     rounds = json_data["data"].get("rounds", [])
#     all_team_keys = set()

#     for rnd in rounds:
#         for group in rnd.get("groups", []):
#             all_team_keys.update(group.get("team_keys", []))

#     assert all_team_keys, "No teams found in tournament groups"
#     assert len(all_team_keys) == 2, f"Tournament is not bilateral (found {len(all_team_keys)} teams)"

#wrong
# tournament is multi-team
# def test_tc_07_tournament_is_multi_team(base_url, valid_headers):

#     key="a-intern-test--cricket--bcci-OFJF--c2-XxGh--2025-0Ye3"

#     url = f"{base_url}{ENDPOINT.format(tournament_key=key)}"
#     response = send_get_request(url, headers=valid_headers)
    
#     assert response.status_code == 200, "Invalid response"
#     json_data = response.json()

#     rounds = json_data["data"].get("rounds", [])
#     all_team_keys = set()

#     for rnd in rounds:
#         for group in rnd.get("groups", []):
#             all_team_keys.update(group.get("team_keys", []))

#     assert all_team_keys, "No teams found in tournament groups"
# assert len(all_team_keys) >= 2, f"Tournament is not multi-team (found {len(all_team_keys)} teams)"



def test_tc_08_rest_match_graphql(valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_FIXTURE_QUERY_FILE = "data/tournament/single_tournament_query.json"

    with open(GRAPHQL_FIXTURE_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key

    graphql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )

    assert graphql_response.status_code == 200, f"GraphQL error: {graphql_response.text}"
