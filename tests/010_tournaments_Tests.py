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

# tours and series are same ,the names can be used to differntiate them 
# Series will have more number of rounds and groups such as round-robin, knockout 

def test_tc_08_rest_match_graphql(valid_headers, graphql_headers, base_url):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_FIXTURE_QUERY_FILE = "data/tournament/single_tournament_query.json"

    with open(GRAPHQL_FIXTURE_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key

    # Make GraphQL request
    graphql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert graphql_response.status_code == 200, f"GraphQL error: {graphql_response.text}"
    graphql_data = graphql_response.json()["data"]["cricket_tournament_detail"]

    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    rest_response = send_get_request(url, headers=valid_headers)
    assert rest_response.status_code == 200, f"Unexpected status code: {rest_response.status_code}"
    rest_data = rest_response.json()["data"]

    gql_tournament = graphql_data["tournament"]
    rest_tournament = rest_data["tournament"]

    assert gql_tournament["key"] == rest_tournament["key"]
    assert gql_tournament["name"] == rest_tournament["name"]
    assert gql_tournament["short_name"] == rest_tournament["short_name"]
    assert gql_tournament["gender"].lower() == rest_tournament["gender"]
    gql_point_system = normalize_string(gql_tournament["point_system"])
    rest_point_system = normalize_string(rest_tournament["point_system"])
    assert gql_point_system == rest_point_system, f"Mismatch in point_system"        
    assert gql_tournament["sport"].lower() == rest_tournament["sport"]

    gql_teams = {team["key"]: team["value"]["name"] for team in graphql_data["teams"]}
    rest_teams = {key: team["name"] for key, team in rest_data["teams"].items()}

    assert gql_teams == rest_teams, f"Team mismatch: GraphQL={gql_teams}, REST={rest_teams}"

    gql_rounds = graphql_data["rounds"]
    rest_rounds = rest_data["rounds"]

    assert len(gql_rounds) == len(rest_rounds), "Number of rounds mismatch"

    for gql_round, rest_round in zip(gql_rounds, rest_rounds):
        assert gql_round["key"] == rest_round["key"]
        assert gql_round["name"] == rest_round["name"]
        assert gql_round["format"].lower() == rest_round["format"]

        gql_groups = gql_round["groups"]
        rest_groups = rest_round["groups"]
        assert len(gql_groups) == len(rest_groups), f"Group count mismatch in round {gql_round['name']}"

        for gql_group, rest_group in zip(gql_groups, rest_groups):
            assert gql_group["key"] == rest_group["key"]
            assert gql_group["name"] == rest_group["name"]

            gql_team_keys = sorted(gql_group["team_keys"])
            rest_team_keys = sorted(rest_group["team_keys"])
            assert gql_team_keys == rest_team_keys, f"Team keys mismatch in group {gql_group['name']}"

            gql_match_keys = sorted(gql_group["match_keys"])
            rest_match_keys = sorted(rest_group["match_keys"])
            assert gql_match_keys == rest_match_keys, f"Match keys mismatch in group {gql_group['name']}"


