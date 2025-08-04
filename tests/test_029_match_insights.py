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
ENDPOINT = "match/{match_key}/insights/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(match_key=MatchState.key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    
    json_data = response.json()

    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    data = json_data["data"]

    for key in ["team_a", "team_b", "recent_h2h", "match", "pitch_report", "top_players"]:
        assert key in data, f"Missing 'data.{key}' field"

    # team
    for team_key in ["team_a", "team_b"]:
        team = data[team_key]
        assert "team" in team, f"Missing '{team_key}.team'"
        assert "recent_matches" in team, f"Missing '{team_key}.recent_matches'"
        assert "squad" in team, f"Missing '{team_key}.squad'"

    # Match
    match = data["match"]
    match_required_fields = [
        "key", "name", "short_name", "sub_title", "status", "start_at",
        "tournament", "metric_group", "sport", "winner", "teams", "venue",
        "expected_start_at", "format", "play_status", "result", "innings"
    ]
    for field in match_required_fields:
        assert field in match, f"Missing match field: {field}"

    # Tournament inside match
    tournament = match["tournament"]
    for field in ["key", "name", "short_name", "alternate_name", "alternate_short_name"]:
        assert field in tournament, f"Missing tournament field: {field}"

    # Teams inside match
    for side in ["a", "b"]:
        team = match["teams"][side]
        team_fields = ["key", "code", "name", "alternate_name", "alternate_code", 
                       "gender_name", "country_code"]
        for field in team_fields:
            assert field in team, f"Missing team.{side} field: {field}"

    # Venue 
    venue = match["venue"]
    venue_fields = ["key", "name", "city", "country", "geolocation"]
    for field in venue_fields:
        assert field in venue, f"Missing venue field: {field}"

    country_fields = ["short_code", "code", "name", "official_name", "is_region"]
    for field in country_fields:
        assert field in venue["country"], f"Missing country field in venue: {field}"

    # Pitch 
    pitch = data["pitch_report"]
    assert "pitch_favours" in pitch, "Missing 'pitch_report.pitch_favours'"
    assert "pitch_favours_bowling" in pitch, "Missing 'pitch_report.pitch_favours_bowling'"

    # Top players
    for player in data["top_players"]:
        assert "player" in player, "Missing top_players.player"
        assert "batting" in player, "Missing top_players.batting"
        assert "bowling" in player, "Missing top_players.bowling"

        batting_fields = ["runs", "balls", "average", "strike_rate"]
        for field in batting_fields:
            assert field in player["batting"], f"Missing batting field: {field}"

        bowling_fields = ["wickets", "runs", "balls", "economy"]
        for field in bowling_fields:
            assert field in player["bowling"], f"Missing bowling field: {field}"


