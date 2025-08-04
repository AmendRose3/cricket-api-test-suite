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

ENDPOINT = "match/{match_key}/over-summary/"

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

def test_tc_05_cricket_over_summaries_structure(base_url, valid_headers):
    """
    Test to validate the structure of cricket match over summaries response.
    This test validates the JSON structure based on the provided sample data.
    """
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()

    # Top-level keys  
    required_top_level_fields = ["data", "cache", "schema", "error", "http_status_code"]
    for field in required_top_level_fields:
        assert field in json_data, f"Missing top-level field: {field}"

    # Data section  
    data = json_data["data"]
    required_data_fields = ["summaries", "previous_page_index", "next_page_index", 
                           "previous_page_key", "next_page_key"]
    for field in required_data_fields:
        assert field in data, f"Missing field in 'data': {field}"

    # Summaries  
    summaries = data["summaries"]
    assert isinstance(summaries, list), "Summaries should be a list"
    assert len(summaries) > 0, "Summaries list should not be empty"

    for summary in summaries:
        # Index  
        assert "index" in summary, "Missing 'index' in summary"
        index = summary["index"]
        assert "innings" in index, "Missing 'innings' in index"
        assert "over_number" in index, "Missing 'over_number' in index"
        assert isinstance(index["over_number"], int), "over_number should be an integer"

        # Basic summary fields
        required_summary_fields = ["runs", "wickets", "strikers", "bowlers", "match_score"]
        for field in required_summary_fields:
            assert field in summary, f"Missing summary field: {field}"

        # Match score  
        match_score = summary["match_score"]
        required_match_score_fields = ["runs", "wickets", "run_rate", "title", "req_runs"]
        for field in required_match_score_fields:
            assert field in match_score, f"Missing match_score field: {field}"
        
        # match score data types
        assert isinstance(match_score["runs"], int), "match_score runs should be integer"
        assert isinstance(match_score["wickets"], int), "match_score wickets should be integer"
        assert isinstance(match_score["run_rate"], (int, float)), "run_rate should be numeric"
        assert isinstance(match_score["title"], str), "title should be string"

        # Strikers  
        strikers = summary["strikers"]
        assert isinstance(strikers, list), "Strikers should be a list"
        assert len(strikers) > 0, "Strikers list should not be empty"

        for striker in strikers:
            assert "player_key" in striker, "Missing player_key in striker"
            assert "score" in striker, "Missing score in striker"
            assert "is_dismissed" in striker, "Missing is_dismissed in striker"
            assert isinstance(striker["is_dismissed"], bool), "is_dismissed should be boolean"

            # Striker score  
            score = striker["score"]
            required_score_fields = ["runs", "balls", "fours", "sixes", "dot_balls", 
                                   "strike_rate", "ones", "twos", "threes", "fives", "stats"]
            for field in required_score_fields:
                assert field in score, f"Missing score field: {field}"

            # Score stats  
            stats = score["stats"]
            required_stats_fields = ["boundary_percentage", "boundary_frequency", 
                                   "dot_ball_percentage", "dot_ball_frequency"]
            for field in required_stats_fields:
                assert field in stats, f"Missing stats field: {field}"
                assert isinstance(stats[field], (int, float)), f"{field} should be numeric"

        # Bowlers  
        bowlers = summary["bowlers"]
        assert isinstance(bowlers, list), "Bowlers should be a list"
        assert len(bowlers) > 0, "Bowlers list should not be empty"

        for bowler in bowlers:
            assert "player_key" in bowler, "Missing player_key in bowler"
            assert "score" in bowler, "Missing score in bowler"

            # Bowler score  
            bowler_score = bowler["score"]
            required_bowler_fields = ["balls", "runs", "economy", "wickets", "extras", 
                                    "maiden_overs", "overs", "balls_breakup", 
                                    "wickets_breakup", "stats"]
            for field in required_bowler_fields:
                assert field in bowler_score, f"Missing bowler score field: {field}"

            # Overs should be a list with exactly 2 elements [completed_overs, balls_in_current_over]
            overs = bowler_score["overs"]
            assert isinstance(overs, list), "Overs should be a list"
            assert len(overs) == 2, "Overs should have exactly 2 elements"

            # Balls breakup  
            balls_breakup = bowler_score["balls_breakup"]
            required_balls_breakup_fields = ["dot_balls", "wides", "no_balls", "fours", "sixes"]
            for field in required_balls_breakup_fields:
                assert field in balls_breakup, f"Missing balls_breakup field: {field}"
                assert isinstance(balls_breakup[field], int), f"{field} should be integer"

            # Wickets breakup  
            wickets_breakup = bowler_score["wickets_breakup"]
            required_wickets_breakup_fields = ["bowled", "caught", "lbw", "stumping"]
            for field in required_wickets_breakup_fields:
                assert field in wickets_breakup, f"Missing wickets_breakup field: {field}"
                assert isinstance(wickets_breakup[field], int), f"{field} should be integer"

        # Extras  
        extras_fields = ["sixes", "fours", "extras", "wides", "no_balls", "leg_byes", "byes"]
        for field in extras_fields:
            assert field in summary, f"Missing extras field: {field}"
            assert isinstance(summary[field], int), f"{field} should be integer"

    # Page navigation  
    if data["previous_page_index"]:
        prev_index = data["previous_page_index"]
        assert "innings" in prev_index, "Missing innings in previous_page_index"
        assert "over_number" in prev_index, "Missing over_number in previous_page_index"

    if data["next_page_index"]:
        next_index = data["next_page_index"]
        assert "innings" in next_index, "Missing innings in next_page_index"
        assert "over_number" in next_index, "Missing over_number in next_page_index"

    # Cache structure  
    cache = json_data["cache"]
    required_cache_fields = ["key", "expires", "etag", "max_age"]
    for field in required_cache_fields:
        assert field in cache, f"Missing cache field: {field}"
    
    assert isinstance(cache["expires"], (int, float)), "expires should be numeric"
    assert isinstance(cache["max_age"], int), "max_age should be integer"

    # Schema versioning  
    schema = json_data["schema"]
    assert "major_version" in schema, "Missing major_version in schema"
    assert "minor_version" in schema, "Missing minor_version in schema"
    assert schema["major_version"] == "5.0", f"Unexpected schema major version: {schema['major_version']}"

    # HTTP status  
    assert json_data["http_status_code"] == 200, f"Invalid HTTP status: {json_data['http_status_code']}"
    assert json_data["error"] is None, f"Error should be None, got: {json_data['error']}"
# _match_summaries_rest_match_graphql

def test_tc_06_rest_graphql_data_match(base_url, valid_headers, graphql_headers):
    import json

    match_key = 'a-intern-test--cricket--KU1950455781946204164'
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"
    GRAPHQL_QUERY_FILE = "data/match/match_summary_query.json"

    # Load GraphQL query
    with open(GRAPHQL_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    # Fetch GraphQL data
    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_summaries = gql_response.json()["data"]["cricket_match_over_summary"]["summaries"]

    # Fetch REST data
    url = f"{base_url}{ENDPOINT.format(match_key=match_key)}"
    rest_response = send_get_request(url, headers=valid_headers)
    assert rest_response.status_code == 200, f"Unexpected REST status: {rest_response.status_code}"
    rest_summaries = rest_response.json()["data"]["summaries"]

    assert isinstance(rest_summaries,list)
    assert isinstance(gql_summaries,list)
    assert len(gql_summaries) == len(rest_summaries), "Summary count mismatch"


    for i in range(len(gql_summaries)):
        gql = gql_summaries[i]
        rest = rest_summaries[i]
        assert normalize_string(gql["index"]["innings"]) == normalize_string(rest["index"]["innings"]), f"Index mismatch at {i}"
        assert normalize_string(gql["index"]["over_number"]) == normalize_string(rest["index"]["over_number"]), f"Index mismatch at {i}"
        assert gql["wickets"] == rest["wickets"], f"Wickets mismatch at {i}"
        assert gql["runs"] == rest["runs"], f"Runs mismatch at {i}"

        gql_keys = sorted([s["player_key"] for s in gql.get("strikers", [])])
        rest_keys = sorted([s["player_key"] for s in rest.get("strikers", [])])
        assert gql_keys == rest_keys, "Mismatch in striker keys"

        for i, (b1, b2) in enumerate(zip(gql.get("bowlers", []), rest.get("bowlers", []))):
            assert b1["player_key"] == b2["player_key"], f"Bowler player_key mismatch at index {i}"

            s1 = b1.get("score", {})
            s2 = b2.get("score", {})

            assert s1.get("runs") == s2.get("runs"), f"Runs mismatch for bowler {b1['player_key']} at index {i}"
            assert s1.get("wickets") == s2.get("wickets"), f"Wickets mismatch for bowler {b1['player_key']} at index {i}"
          
            gql_score = gql.get("match_score", {})
            rest_score = rest.get("match_score", {})

            assert gql_score.get("runs") == rest_score.get("runs"), "Mismatch in match_score runs"
            assert gql_score.get("wickets") == rest_score.get("wickets"), "Mismatch in match_score wickets"



def test_tc_07_over_summary_pagination(base_url,valid_headers):
    match_key = "a-intern-test--cricket--KU1950455781946204164"
    current_key = "b_1_1"

    url1 = f"{base_url}match/{match_key}/over-summary/{current_key}/"
    print(url1)
    res1 =send_get_request(url1, headers=valid_headers)
    assert res1.status_code == 200
    data1 = res1.json().get("data", {})

    next_page_key = data1.get("next_page_key")
    assert next_page_key, f"No next_page_key found in response for {current_key}"

    url2 = f"{base_url}match/{match_key}/over-summary/{next_page_key}/"
    res2 = send_get_request(url2, headers=valid_headers)
    assert res2.status_code == 200
    data2 = res2.json().get("data", {})

    previous_page_key = data2.get("previous_page_key")
    assert previous_page_key == current_key, (
        f"Expected previous_page_key to be {current_key}, got {previous_page_key}"
    )


