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

ENDPOINT = "tournament/{tournament_key}/team/{team_key}/"
UNANNOUNCED_SQUAD_TOURNAMENT_KEY="a-intern-test--cricket--isa2j-Srxj--is2j-GrV8--2026-J5nI"
UNANNOUNCED_SQUAD_TEAM_KEY="a-intern-test--cricket--csk-a43S"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(tournament_key=TournamentState.key,team_key=TournamentState.team_key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)


def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)


def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_tournament_team_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key,team_key=TournamentState.team_key)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    json_data = response.json()

    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    # Team
    team = json_data["data"].get("team")
    assert isinstance(team, dict), "'team' should be a dict"
    for field in ["key", "code", "name", "alternate_name", "alternate_code", "gender_name"]:
        assert field in team, f"Missing field in team: {field}"

    # Tournament
    tournament = json_data["data"].get("tournament")
    assert isinstance(tournament, dict), "'tournament' should be a dict"
    for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
        assert field in tournament, f"Missing field in tournament: {field}"

    # Tournament Team
    tournament_team = json_data["data"].get("tournament_team")
    assert isinstance(tournament_team, dict), "'tournament_team' should be a dict"

    # Players
    players = tournament_team.get("players")
    assert isinstance(players, dict), "'players' should be a dict"
    for player_key, player in players.items():
        assert isinstance(player, dict), f"Player {player_key} should be a dict"
        for field in [
            "key", "name", "jersey_name", "legal_name", "gender",
            "nationality", "seasonal_role", "batting_style", "skills",
            "legal_name_v2", "jersey_name_v2"
        ]:
            assert field in player, f"Missing field in player: {field}"

        nationality = player.get("nationality")
        assert isinstance(nationality, dict), f"'nationality' in player {player_key} should be a dict"
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert field in nationality, f"Missing nationality field in player {player_key}: {field}"

    # player_keys
    assert isinstance(tournament_team.get("player_keys"), list), "'player_keys' should be a list"

    # captain_keys and keeper_keys
    for field in ["captain_keys", "keeper_keys"]:
        assert field in tournament_team, f"Missing field: {field}"
        assert isinstance(tournament_team.get(field), list), f"'{field}' should be a list"

    # players_by_format
    players_by_format = tournament_team.get("players_by_format")
    assert isinstance(players_by_format, dict), "'players_by_format' should be a dict"
    for format_key in ["t20", "oneday", "test", "t10", "hundred_ball", "sixty_ball"]:
        assert format_key in players_by_format, f"Missing format in players_by_format: {format_key}"
        format_value = players_by_format[format_key]
        assert format_value is None or isinstance(format_value, list), f"{format_key} should be a list or null"



def test_tc_06_rest_vs_graphql_tournament_team(valid_headers, graphql_headers, base_url):
    # REST API request
    rest_url = f"{base_url}{ENDPOINT.format(tournament_key=TournamentState.key,team_key=TournamentState.team_key)}"
    response = send_get_request(rest_url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    rest_data = response.json()["data"]

    # GraphQL request
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_QUERY_FILE = "data/tournament/tournament_team_query.json"

    with open(GRAPHQL_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["key"] = TournamentState.key
    gql_payload["variables"]["teamKey"] = TournamentState.team_key

    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL failed: {gql_response.text}"
    gql_data = gql_response.json()["data"]["cricket_tournament_team"]

    # Compare basic team details
    for field in ["key", "code", "name"]:
        assert gql_data["team"][field] == rest_data["team"][field], f"Mismatch in team {field}"

    for field in ["key", "name", "short_name"]:
        assert gql_data["tournament"][field] == rest_data["tournament"][field], f"Mismatch in tournament {field}"

    gql_team = gql_data["tournament_team"]
    rest_team = rest_data["tournament_team"]

    # Compare player_keys, captain_keys, keeper_keys
    for field in ["player_keys", "captain_keys", "keeper_keys"]:
        assert sorted(gql_team[field]) == sorted(rest_team[field]), f"Mismatch in {field}"

    # Compare players_by_format
    for fmt in ["t20", "oneday", "test", "t10", "hundred_ball", "sixty_ball"]:
        gql_fmt = gql_team["players_by_format"].get(fmt)
        rest_fmt = rest_team["players_by_format"].get(fmt)
        if gql_fmt is None and rest_fmt is None:
            continue
        assert sorted(gql_fmt) == sorted(rest_fmt), f"Mismatch in players_by_format[{fmt}]"

    # Compare players
    gql_players = {player["key"]: player["value"] for player in gql_team["players"]}
    rest_players = rest_team["players"]

    assert gql_players.keys() == rest_players.keys(), "Mismatch in player keys"

    for key in gql_players:
        gql_p = gql_players[key]
        rest_p = rest_players[key]

        # Basic player details
        for field in [
            "key", "name", "jersey_name", "legal_name", "legal_name_v2", "jersey_name_v2",
            "gender", "seasonal_role", "batting_style", "bowling_style"
        ]:
            gql_val = normalize_string(gql_p.get(field))
            rest_val = normalize_string(rest_p.get(field))
            assert gql_val == rest_val, f"Mismatch in field '{field}' for player {key}"

        # Skills comparison
        gql_skills = sorted([normalize_string(s) for s in gql_p.get("skills", [])])
        rest_skills = sorted([normalize_string(s) for s in rest_p.get("skills", [])])
        assert gql_skills == rest_skills, f"Mismatch in skills for player {key}"

        # Nationality comparison
        gql_nat = gql_p["nationality"]
        rest_nat = rest_p["nationality"]
        for field in ["short_code", "code", "name", "official_name", "is_region"]:
            assert gql_nat[field] == rest_nat[field], f"Mismatch in nationality.{field} for player {key}"



# Scenario where sqaud is not announced (players list will be empty)

def test_tc_07_tournament_team_unannounced(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(tournament_key=UNANNOUNCED_SQUAD_TOURNAMENT_KEY,team_key=UNANNOUNCED_SQUAD_TEAM_KEY)}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    json_data = response.json()

    # Team
    team = json_data["data"].get("team")
    assert isinstance(team, dict), "'team' should be a dict"
    assert team is not None,"team is not empty since team is declared"
    assert team["key"] is not None
    assert team["code"] is not None
    assert team["name"] is not None


    # Tournament
    tournament = json_data["data"].get("tournament")
    assert isinstance(tournament, dict), "'tournament' should be a dict"
    assert tournament["key"] is not None
    assert tournament ["name"] is not None

    # Tournament Team
    tournament_team = json_data["data"].get("tournament_team")
    print(tournament_team)
    assert isinstance(tournament_team, dict), "'tournament_team' should be a dict"
    assert not tournament_team["players"], "Expected no players to be announced yet"
    assert not tournament_team["player_keys"],"Since players are not announced, not expecting players in the list"
   
