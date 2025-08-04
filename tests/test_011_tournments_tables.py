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

ENDPOINT = "tournament/{tournament_key}/points/"


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

    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    # Tournament
    tournament = json_data["data"].get("tournament")
    assert isinstance(tournament, dict), "'tournament' should be a dict"
    for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
        assert field in tournament, f"Missing field in tournament: {field}"

    # Rounds
    rounds = json_data["data"].get("rounds")
    assert isinstance(rounds, list), "'rounds' should be a list"

    for rnd in rounds:
        tr = rnd.get("tournament_round")
        assert isinstance(tr, dict), "'tournament_round' should be a dict"
        for field in ["key", "name"]:
            assert field in tr, f"Missing field in tournament_round: {field}"

        groups = rnd.get("groups")
        assert isinstance(groups, list), "'groups' should be a list"

        for group in groups:
            grp = group.get("group")
            assert isinstance(grp, dict), "'group' should be a dict"
            for field in ["key", "name"]:
                assert field in grp, f"Missing field in group: {field}"

            points = group.get("points")
            assert isinstance(points, list), "'points' should be a list"

            for team_data in points:
                team = team_data.get("team")
                assert isinstance(team, dict), "'team' should be a dict"
                for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name"]:
                    assert field in team, f"Missing field in team: {field}"

                for field in ["position_in_table", "played", "won", "lost", "tied", "draw", "no_result", "points", "net_run_rate"]:
                    assert field in team_data, f"Missing field in points entry: {field}"

def test_tc_09_tournament_points_rest_vs_graphql(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_POINTS_QUERY_FILE = "data/tournament/points_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key

    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_data = gql_response.json()["data"]["cricket_tournament_points"]

    # REST request
    rest_url =f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST error: {rest_response.text}"
    rest_data = rest_response.json()["data"]

    # Tournament Info
    for field in ["key", "name", "short_name"]:
        assert gql_data["tournament"][field] == rest_data["tournament"][field], f"Mismatch in tournament.{field}"

    gql_rounds = gql_data["rounds"]
    rest_rounds = rest_data["rounds"]
    assert len(gql_rounds) == len(rest_rounds), "Mismatch in number of rounds"

    for gql_round, rest_round in zip(gql_rounds, rest_rounds):
        gql_round_info = gql_round["tournament_round"]
        rest_round_info = rest_round["tournament_round"]

        assert gql_round_info["key"] == rest_round_info["key"], f"Mismatch in round key"
        assert gql_round_info["name"] == rest_round_info["name"], f"Mismatch in round name"

        gql_groups = gql_round["groups"]
        rest_groups = rest_round["groups"]
        assert len(gql_groups) == len(rest_groups), f"Mismatch in number of groups in round {gql_round_info['name']}"

        for gql_group, rest_group in zip(gql_groups, rest_groups):
            gql_group_info = gql_group["group"]
            rest_group_info = rest_group["group"]

            assert gql_group_info["key"] == rest_group_info["key"], f"Group key mismatch"
            assert gql_group_info["name"] == rest_group_info["name"], f"Group name mismatch"

            gql_points = gql_group["points"]
            rest_points = rest_group["points"]
            assert len(gql_points) == len(rest_points), f"Mismatch in number of teams in group {gql_group_info['name']}"

            for gql_team_data, rest_team_data in zip(gql_points, rest_points):
                gql_team = gql_team_data["team"]
                rest_team = rest_team_data["team"]

                # team identity
                for field in ["key", "code", "name"]:
                    assert gql_team[field] == rest_team[field], f"Mismatch in team.{field} for {gql_team['key']}"

                # points data
                for field in ["position_in_table", "played", "won", "lost", "tied", "draw", "no_result", "points", "net_run_rate"]:
                    assert gql_team_data[field] == rest_team_data[field], f"Mismatch in points field '{field}' for team {gql_team['key']} in group {gql_group_info['name']}"
