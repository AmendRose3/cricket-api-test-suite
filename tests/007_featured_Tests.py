import pytest, requests, json
from utils.request_handler import send_get_request, make_graphql_request
from utils.common import normalize_string
from tests.state import AssociationState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)

ENDPOINT = "featured-tournaments/"


def test_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)


def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)


def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)


def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_get_featured_tournaments_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"

    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data.get("http_status_code") == 200, "'http_status_code' is not 200"
    assert "data" in json_data, "'data' key missing in response"
    assert "tournaments" in json_data["data"], "'tournaments' key missing in data"

    tournaments = json_data["data"]["tournaments"]
    assert isinstance(tournaments, list), "'tournaments' should be a list"

    for tournament in tournaments:
        for field in [
            "key", "name", "short_name", "start_date", "gender",
            "point_system", "competition", "association_key", "sport",
            "is_date_confirmed", "is_venue_confirmed",
            "last_scheduled_match_date", "formats", "countries"
        ]:
            assert field in tournament, f"'{field}' missing in tournament"

        assert isinstance(tournament["competition"], dict), "'competition' should be a dict"
        for field in ["key", "code", "name"]:
            assert field in tournament["competition"], f"'{field}' missing in competition"

        assert isinstance(tournament["countries"], list), "'countries' should be a list"
        for country in tournament["countries"]:
            for field in ["short_code", "code", "name", "official_name", "is_region"]:
                assert field in country, f"'{field}' missing in country"


def test_tc_06_featured_tournament_keys_match(graphql_headers, valid_headers, base_url):
    GRAPHQL_PAYLOAD_FILE = "data/tournament/featured_query.json"

    with open(GRAPHQL_PAYLOAD_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"] = {}

    graphql_url = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    graphql_response = make_graphql_request(
        url=graphql_url,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )

    assert graphql_response.status_code == 200, f"GraphQL error: {graphql_response.text}"
    graphql_data = graphql_response.json()["data"]["cricket_featured_tournaments"]["tournaments"]
    assert isinstance(graphql_data, list) and graphql_data, "GraphQL: Tournament list empty"

    rest_url = url = f"{base_url}{ENDPOINT}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST error: {rest_response.text}"
    rest_data = rest_response.json()["data"]["tournaments"]

    rest_dict = {item["key"]: item for item in rest_data}

        # Check for unprecedented times (off-season, pandemic, etc.)
    if not graphql_data:
        print("No tournaments — this may be an off-season or special case (e.g., pandemic).")
        assert rest_data == [], "REST should also return empty list during unprecedented times"
        return  
    else:
        gql_count = len(graphql_data)
        # Normal or busy season
        if 1 <= gql_count <= 20:
            print("Normal season: Expected number of tournaments (1-20).")
        elif gql_count >= 21:
            print("Busy season: Higher tournament count (more that 20).")
            assert gql_count >= 21, "Expected busy season with more than 20 tournaments"

    for gql_tournament in graphql_data:
        tournament_key = gql_tournament["key"]
        assert tournament_key in rest_dict, f"Tournament key {tournament_key} missing in REST"
        rest_tournament = rest_dict[tournament_key]
        assert gql_tournament["competition"]["key"] == rest_tournament["competition"]["key"], f"Competition key mismatch for {tournament_key}"
        assert gql_tournament["name"] == rest_tournament["name"], f"Mismatch in name for {tournament_key}"
        assert gql_tournament["short_name"] == rest_tournament["short_name"], f"Mismatch in short_name for {tournament_key}"
        assert gql_tournament["association_key"] == rest_tournament["association_key"], f"Mismatch in association_key for {tournament_key}"
        assert gql_tournament["competition"]["key"] == rest_tournament["competition"]["key"], f"Mismatch in competition.key for {tournament_key}"
        assert gql_tournament["competition"]["name"] == rest_tournament["competition"]["name"], f"Mismatch in competition.name for {tournament_key}"
        assert gql_tournament["start_date"] == rest_tournament["start_date"], f"Mismatch in start_date for {tournament_key}"
        assert gql_tournament["gender"].lower() == rest_tournament["gender"].lower(), f"Mismatch in gender for {tournament_key}"
        gql_point_system = normalize_string(gql_tournament["point_system"])
        rest_point_system = normalize_string(rest_tournament["point_system"])
        assert gql_point_system == rest_point_system, f"Mismatch in point_system for {tournament_key}: GQL={gql_point_system}, REST={rest_point_system}"        
        assert gql_tournament["metric_group"] == rest_tournament["metric_group"], f"Mismatch in metric_group for {tournament_key}"
        assert gql_tournament["sport"].lower() == rest_tournament["sport"].lower(), f"Mismatch in sport for {tournament_key}"
        assert gql_tournament["is_date_confirmed"] == rest_tournament["is_date_confirmed"], f"Mismatch in is_date_confirmed for {tournament_key}"
        assert gql_tournament["is_venue_confirmed"] == rest_tournament["is_venue_confirmed"], f"Mismatch in is_venue_confirmed for {tournament_key}"
        assert gql_tournament["last_scheduled_match_date"] == rest_tournament["last_scheduled_match_date"], f"Mismatch in last_scheduled_match_date for {tournament_key}"
        gql_formats = sorted([fmt.lower() for fmt in gql_tournament["formats"]])
        rest_formats = sorted([fmt.lower() for fmt in rest_tournament["formats"]])
        assert gql_formats == rest_formats, f"Mismatch in formats for {tournament_key}"

        #True fields
        assert gql_tournament["is_date_confirmed"] == rest_tournament["is_date_confirmed"] == True, f" is_date_confirmed is false for {tournament_key}"
        assert gql_tournament["is_venue_confirmed"] == rest_tournament["is_venue_confirmed"] == True, f"is_venue_confirmed is false for {tournament_key}"



