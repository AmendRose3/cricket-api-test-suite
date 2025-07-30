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

ENDPOINT = "fixtures/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    run_valid_token_authentication(ENDPOINT.format(match_key=MatchState.key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_month_fixtures_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()

    # Top-level keys
    for key in ["data", "cache", "schema", "error", "http_status_code"]:
        assert key in json_data, f"Missing top-level key: {key}"

    data = json_data["data"]
    for key in ["month", "prev_month", "next_month", "current_month"]:
        assert key in data, f"Missing key in 'data': {key}"

    month_data = data["month"]
    for key in ["month", "current_month", "days"]:
        assert key in month_data, f"Missing key in 'month': {key}"

    assert isinstance(month_data["days"], list), "'days' should be a list"

    for day in month_data["days"]:
        assert "day" in day, "Missing 'day' key in day object"
        assert "current_day" in day, "Missing 'current_day' in day object"
        assert "matches" in day, "Missing 'matches' in day object"
        assert isinstance(day["matches"], list), "'matches' should be a list"

        for match in day["matches"]:
            for field in [
                "key", "name", "short_name", "sub_title", "status", "start_at",
                "tournament", "sport", "winner", "teams", "venue", "association",
                "gender", "format", "estimated_end_date", "completed_date_approximate"
            ]:
                assert field in match, f"Missing field in match: {field}"

            # Tournament
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
            if venue:
                for field in ["key", "name", "city", "country", "geolocation"]:
                    assert field in venue, f"Missing field in venue: {field}"
                country = venue["country"]
                if country:
                    for field in ["short_code", "code", "name", "official_name", "is_region"]:
                        assert field in country, f"Missing field in venue.country: {field}"

            # Association
            association = match["association"]
            if association:
                for field in ["key", "code", "name", "country", "parent"]:
                    assert field in association, f"Missing field in association: {field}"
