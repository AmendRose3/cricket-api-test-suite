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

T20_key="a-intern-test--cricket--Ca1950061585179525124"
ODI_key="a-intern-test--cricket--du1950148740761440259"
Test_key="a-intern-test--cricket--qo1950156409505226755"
live_match_key="a-intern-test--cricket--Ca1949722003183411201"
completed_match_key='a-intern-test--cricket--yc1950078336558616577'
upcoming_key="a-intern-test--cricket--0Q1949781585960280066"
super_over_key="a-intern-test--cricket--0U1950433793362022404"
# delayed_start=""
drawn_match_key="a-intern-test--cricket--KU1950455781946204164"
Abandoned_match_key="a-intern-test--cricket--Z41951155191541829634"

ENDPOINT = "match/{match_key}/"

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

def test_tc_05_matches_detail_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    
    #   top-level structure
    assert "data" in json_data, "Missing 'data' field"
    assert "cache" in json_data, "Missing 'cache' field"
    assert "schema" in json_data, "Missing 'schema' field"
    assert "error" in json_data, "Missing 'error' field"
    assert "http_status_code" in json_data, "Missing 'http_status_code' field"
    
    data = json_data["data"]
    
    #   main match data fields
    required_fields = [
        "key", "name", "short_name", "sub_title", "status", "start_at",
        "tournament", "metric_group", "sport", "winner", "teams", "venue",
        "association", "messages", "gender", "format", "title", "play_status",
        "toss", "play", "players", "notes", "data_review", "squad"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    #   tournament structure
    tournament = data["tournament"]
    tournament_fields = ["key", "name", "short_name", "alternate_name", "alternate_short_name"]
    for field in tournament_fields:
        assert field in tournament, f"Missing tournament field: {field}"
    
    #   teams structure
    teams = data["teams"]
    assert "a" in teams, "Missing team 'a'"
    assert "b" in teams, "Missing team 'b'"
    
    for team_key in ["a", "b"]:
        team = teams[team_key]
        team_fields = ["key", "code", "name", "alternate_name", "alternate_code", 
                      "gender_name", "country_code"]
        for field in team_fields:
            assert field in team, f"Missing team {team_key} field: {field}"
    
    #   venue structure
    venue = data["venue"]
    venue_fields = ["key", "name", "city", "country", "geolocation"]
    for field in venue_fields:
        assert field in venue, f"Missing venue field: {field}"
    
    #   country structure within venue
    country = venue["country"]
    country_fields = ["short_code", "code", "name", "official_name", "is_region"]
    for field in country_fields:
        assert field in country, f"Missing venue country field: {field}"
    
    #   association structure
    association = data["association"]
    association_fields = ["key", "code", "name", "country", "parent"]
    for field in association_fields:
        assert field in association, f"Missing association field: {field}"
    
    #   toss structure
    toss = data["toss"]
    toss_fields = ["called", "winner", "elected", "squad_announced"]
    for field in toss_fields:
        assert field in toss, f"Missing toss field: {field}"
    
    #   play structure
    play = data["play"]
    play_fields = ["first_batting", "day_number", "overs_per_innings", "reduced_overs",
                   "target", "result", "innings_order", "innings", "live", "related_balls"]
    for field in play_fields:
        assert field in play, f"Missing play field: {field}"
    
    #   target structure
    target = play["target"]
    target_fields = ["balls", "runs", "dl_applied"]
    for field in target_fields:
        assert field in target, f"Missing target field: {field}"
    
    #   result structure
    result = play["result"]
    result_fields = ["pom", "winner", "result_type", "win_by", "msg"]
    for field in result_fields:
        assert field in result, f"Missing result field: {field}"
    
    #   innings structure
    innings = play["innings"]
    assert isinstance(innings, dict), "Innings should be a dictionary"
    
    # Check innings structure for both innings
    for innings_key in innings:
        innings_data = innings[innings_key]
        innings_fields = ["index", "overs", "is_completed", "score_str", "score",
                         "score_breakup_detail", "wickets", "extra_runs", "balls_breakup",
                         "batting_order", "bowling_order", "wicket_order", "partnerships"]
        for field in innings_fields:
            assert field in innings_data, f"Missing innings {innings_key} field: {field}"
        
        #   score structure within innings
        score = innings_data["score"]
        score_fields = ["runs", "balls", "fours", "sixes", "dot_balls", "run_rate"]
        for field in score_fields:
            assert field in score, f"Missing innings {innings_key} score field: {field}"
        
        #   extra_runs structure
        extra_runs = innings_data["extra_runs"]
        extra_fields = ["extra", "bye", "leg_bye", "wide", "no_ball", "penalty"]
        for field in extra_fields:
            assert field in extra_runs, f"Missing innings {innings_key} extra_runs field: {field}"
    
    #   live data structure
    live = play["live"]
    live_fields = ["innings", "batting_team", "bowling_team", "last_ball_key",
                   "striker_key", "non_striker_key", "bowler_key", "match_break",
                   "score", "required_score", "recent_overs", "recent_overs_repr",
                   "recent_players", "session", "remaining_day_overs"]
    for field in live_fields:
        assert field in live, f"Missing live field: {field}"
    
    #   live score structure
    live_score = live["score"]
    live_score_fields = ["runs", "balls", "wickets", "run_rate", "title", "overs",
                        "msg_lead_by", "msg_trail_by"]
    for field in live_score_fields:
        assert field in live_score, f"Missing live score field: {field}"
    
    #   recent_players structure
    recent_players = live["recent_players"]
    player_types = ["striker", "non_striker", "bowler"]
    for player_type in player_types:
        if player_type in recent_players and recent_players[player_type]:
            player = recent_players[player_type]
            player_fields = ["key", "name", "stats"]
            for field in player_fields:
                assert field in player, f"Missing recent_players {player_type} field: {field}"
    
    #   players structure
    players = data["players"]
    assert isinstance(players, dict), "Players should be a dictionary"
    
    # Check at least one player structure
    if players:
        player_key = next(iter(players))
        player_data = players[player_key]
        assert "player" in player_data, f"Missing 'player' field for player {player_key}"
        assert "score" in player_data, f"Missing 'score' field for player {player_key}"
        
        #   player info structure
        player_info = player_data["player"]
        player_info_fields = ["key", "name", "jersey_name", "legal_name", "gender",
                             "nationality", "seasonal_role", "roles", "batting_style",
                             "bowling_style", "skills"]
        for field in player_info_fields:
            assert field in player_info, f"Missing player info field: {field}"
        
        #   nationality structure
        nationality = player_info["nationality"]
        nationality_fields = ["short_code", "code", "name", "official_name", "is_region"]
        for field in nationality_fields:
            assert field in nationality, f"Missing nationality field: {field}"
    
    #   squad structure
    squad = data["squad"]
    for team_key in ["a", "b"]:
        assert team_key in squad, f"Missing squad for team {team_key}"
        team_squad = squad[team_key]
        squad_fields = ["player_keys", "captain", "keeper", "playing_xi", "replacements"]
        for field in squad_fields:
            assert field in team_squad, f"Missing squad {team_key} field: {field}"
    
    #   data_review structure
    data_review = data["data_review"]
    review_fields = ["schedule", "venue", "result", "pom", "score", "players",
                    "playing_xi", "score_reviewed_ball_index", "team_a", "team_b",
                    "good_to_close", "note"]
    for field in review_fields:
        assert field in data_review, f"Missing data_review field: {field}"
    
    #   cache structure
    cache = json_data["cache"]
    cache_fields = ["key", "expires", "etag", "max_age"]
    for field in cache_fields:
        assert field in cache, f"Missing cache field: {field}"
    
    #   schema structure
    schema = json_data["schema"]
    schema_fields = ["major_version", "minor_version"]
    for field in schema_fields:
        assert field in schema, f"Missing schema field: {field}"
    
    #   data types for critical fields
    assert isinstance(data["start_at"], (int, float)), "start_at should be numeric"
    assert isinstance(data["status"], str), "status should be string"
    assert isinstance(data["sport"], str), "sport should be string"
    assert isinstance(data["format"], str), "format should be string"
    assert isinstance(data["gender"], str), "gender should be string"
    assert isinstance(json_data["http_status_code"], int), "http_status_code should be integer"
    
    #   overs_per_innings is a list for T20 and oneday but Null for test
    if(data["format"]=='test'):
        assert play["overs_per_innings"] is None, "overs_per_innings should be a list"
    else:
        assert isinstance(play["overs_per_innings"], list), "overs_per_innings should be a list"
        assert len(play["overs_per_innings"]) == 2, "overs_per_innings should have 2 elements"
    
    #   innings_order is a list
    assert isinstance(play["innings_order"], list), "innings_order should be a list"
    

def test_tc_06_T20_match(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=T20_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["format"]=='t20', "format is not T20"
    assert data["play"]["overs_per_innings"][0] == 20, "T20 has 20 over per innings, but shows a different result"


def test_tc_06_ODI_match_structure(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=ODI_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["format"]=='oneday', "format is not T20"
    assert data["play"]["overs_per_innings"][0] == 50, "ODI has 50 over per innings, but shows a different result"

def test_tc_06_test_match_structure(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=Test_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["format"]=='test', "format is not T20"
    # assert not data["play"]["overs_per_innings"], "Doubt"


def test_tc_07_live_match(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=live_match_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["status"]=='started', "Live match status"


def test_tc_08_completed_match(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=completed_match_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["status"]=='completed', "completed match status should be completed"
    assert  data["winner"], "winner is not declared, but match is completed"

def test_tc_09_upcoming_match(base_url,valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=upcoming_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()
    data = json_data["data"]
    assert data["status"]=='not_started', "upcoming match status should be not_started"
    assert  not data["winner"], "winner is declared, but match is not started"


def test_tc_10_super_over_match(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=super_over_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.json().get("data")
    assert data.get("status") == "completed", "Super over validation is only applicable to completed matches"

    play = data.get("play")
    result = play.get("result")
    assert result is not None, "Expected result to be present, got None"
    assert result.get("result_type") == "tie_breaker", f"Expected result_type to be 'tie_breaker', got {result.get('result_type')}"

    innings = play.get("innings")
    assert "a_superover" in innings or "b_superover" in innings, "Super over innings not found"

# Obtain the ball keys of three all recently bowled overs using the recent_overs property under the live object
# related_balls object gives complete details

def test_tc_11_recently_bowled_match(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=super_over_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.json().get("data")

    play = data.get("play", {})
    live = play.get("live", {})
    related_balls = play.get("related_balls", {})

    assert live, "Expected 'live' object in play"
    assert "recent_overs" in live, "Missing 'recent_overs' in live"
    recent_overs = live["recent_overs"]
    assert isinstance(recent_overs, list) and recent_overs, "recent_overs should be a non-empty list"

    last_3_overs = recent_overs[-3:]

    for over in last_3_overs:
        overnumber = over.get("overnumber")
        over_key = over.get("over_key")
        ball_keys = over.get("ball_keys", [])

        assert overnumber is not None, "Over must have an 'overnumber'"
        assert over_key, "Over must have an 'over_key'"
        assert isinstance(ball_keys, list) and ball_keys, f"Over {overnumber} has no ball_keys"

        for bk in ball_keys:
            assert bk in related_balls, f"Ball key {bk} not found in related_balls"

            ball_info = related_balls[bk]

            # Basic checks
            assert ball_info["key"] == bk, f"Mismatch in ball key {bk}"
            assert "overs" in ball_info, f"No 'overs' info for ball {bk}"
            assert isinstance(ball_info["overs"], list) and len(ball_info["overs"]) == 2, f"Invalid overs format in ball {bk}"

            # Validate innings match
            innings = live.get("innings")
            assert ball_info["innings"] == innings, f"Innings mismatch in ball {bk}: expected {innings}, got {ball_info['innings']}"


#Drawn Match

def test_tc_12_drawn_match(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=drawn_match_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.json().get("data")
    assert data.get("status") == "completed", "Draw match validation is only applicable to completed matches"

    play = data.get("play")
    assert play is not None, "Expected 'play' data, got None"

    result = play.get("result")
    assert result is not None, "Expected result to be present, got None"
    assert result.get("result_type") == "draw", f"Expected result_type to be 'draw', got {result.get('result_type')}"
    assert result.get("winner") is None, "Expected no winner in a draw match"

    innings = play.get("innings")
    assert "a_1" in innings and "b_1" in innings, "Both innings (a_1 and b_1) should be present in a draw match"

    score_a = innings["a_1"]["score"]["runs"]
    score_b = innings["b_1"]["score"]["runs"]
    assert score_a == score_b, f"Expected equal scores for draw match, got {score_a} and {score_b}"




def test_tc_13_match_featured_rest_vs_graphql(base_url, valid_headers, graphql_headers):
    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_POINTS_QUERY_FILE = "data/match/match_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"]["matchKey"] = MatchState.key

    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_match = gql_response.json()["data"]["cricket_match"]
    test_key=gql_match.get('key')

    rest_url = f"{base_url}{ENDPOINT.format(match_key=test_key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_match = rest_response.json()["data"]


    assert gql_match["key"] == rest_match["key"], "Mismatch in match key"
    assert gql_match["name"] == rest_match["name"], "Mismatch in match name"
    assert gql_match["short_name"] == rest_match["short_name"], "Mismatch in short_name"
    assert gql_match["sub_title"] == rest_match["sub_title"], "Mismatch in sub_title"
    assert gql_match["status"].lower() == rest_match["status"].lower(), "Mismatch in status"
    assert gql_match["start_at"] == rest_match["start_at"], "Mismatch in start_at"
    assert gql_match["metric_group"] == rest_match["metric_group"], "Mismatch in metric_group"
    assert gql_match["sport"].lower() == rest_match["sport"].lower(), "Mismatch in sport"
    assert (gql_match["winner"] or "").lower() == (rest_match["winner"] or "").lower(), "Mismatch in winner"
    assert gql_match["gender"].lower() == rest_match["gender"].lower(), "Mismatch in gender"
    assert gql_match["format"].lower() == rest_match["format"].lower(), "Mismatch in format"
    assert gql_match["title"] == rest_match["title"], "Mismatch in title"
    assert gql_match["play_status"].lower() == rest_match["play_status"].lower(), "Mismatch in play_status"

    gql_tournament = gql_match["tournament"]
    rest_tournament = rest_match["tournament"]
    assert gql_tournament["key"] == rest_tournament["key"], "Mismatch in tournament key"
    assert gql_tournament["name"] == rest_tournament["name"], "Mismatch in tournament name"
    assert gql_tournament["short_name"] == rest_tournament["short_name"], "Mismatch in tournament short_name"

    gql_venue = gql_match["venue"]
    rest_venue = rest_match["venue"]
    assert gql_venue["key"] == rest_venue["key"], "Mismatch in venue key"
    assert gql_venue["name"] == rest_venue["name"], "Mismatch in venue name"

    gql_assoc = gql_match["association"]
    rest_assoc = rest_match["association"]
    assert gql_assoc["key"] == rest_assoc["key"], "Mismatch in association key"
    assert gql_assoc["code"] == rest_assoc["code"], "Mismatch in association code"
    assert gql_assoc["name"] == rest_assoc["name"], "Mismatch in association name"
    if gql_assoc.get("country") and rest_assoc.get("country"):
        assert gql_assoc["country"]["code"] == rest_assoc["country"]["code"], "Mismatch in association country code"

    gql_teams = {team["key"].lower(): team["value"] for team in gql_match["teams"]}
    rest_teams = rest_match["teams"]

    for team_key in gql_teams:
        gql_team = gql_teams[team_key]
        rest_team = rest_teams.get(team_key)
        assert rest_team is not None, f"Team {team_key} missing in REST response"
        assert gql_team["key"] == rest_team["key"], f"Mismatch in team key for {team_key}"
        assert gql_team["code"] == rest_team["code"], f"Mismatch in team code for {team_key}"
        assert gql_team["name"] == rest_team["name"], f"Mismatch in team name for {team_key}"
        assert gql_team["country_code"] == rest_team.get("country_code"), f"Mismatch in team country_code for {team_key}"


def test_tc_14_abandoned_match(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=Abandoned_match_key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.json().get("data")
    assert data.get("play_status") == "abandoned", "Match is expected to be abandoned"
