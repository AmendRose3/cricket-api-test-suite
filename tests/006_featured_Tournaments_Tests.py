
import pytest,requests,json
from utils.request_handler import send_get_request,send_post_request,make_graphql_request
from tests.state import AssociationState
from pathlib import Path
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)

ENDPOINT = "association/{key}/featured-tournaments/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT.format(key=AssociationState.key), base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_05_get_featured_tournaments_valid(base_url, valid_headers):

    url = f"{base_url}{ENDPOINT.format(key=AssociationState.key)}"

    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()

    assert json_data.get("http_status_code") == 200, "'http_status_code' is not 200"
    assert "data" in json_data, "'data' key missing in response"
    assert "tournaments" in json_data["data"], "'tournaments' key missing in data"

    tournaments = json_data["data"]["tournaments"]
    assert isinstance(tournaments, list), "'tournaments' should be a list"

    for tournament in tournaments:
        assert "key" in tournament, "'key' missing in tournament"
        assert "name" in tournament, "'name' missing in tournament"
        assert "short_name" in tournament, "'short_name' missing in tournament"
        assert "start_date" in tournament, "'start_date' missing in tournament"
        assert "gender" in tournament, "'gender' missing in tournament"
        assert "point_system" in tournament, "'point_system' missing in tournament"
        assert "competition" in tournament, "'competition' missing in tournament"
        assert "association_key" in tournament, "'association_key' missing in tournament"
        assert "sport" in tournament, "'sport' missing in tournament"
        assert "is_date_confirmed" in tournament, "'is_date_confirmed' missing in tournament"
        assert "is_venue_confirmed" in tournament, "'is_venue_confirmed' missing in tournament"
        assert "last_scheduled_match_date" in tournament, "'last_scheduled_match_date' missing"
        assert "formats" in tournament and isinstance(tournament["formats"], list), "'formats' should be a list"
        assert "tour_key" in tournament, "'tour_key' missing in tournament"
        assert "countries" in tournament and isinstance(tournament["countries"], list), "'countries' should be a list"

        competition = tournament["competition"]
        assert isinstance(competition, dict), "'competition' should be a dict"
        assert "key" in competition, "'key' missing in competition"
        assert "code" in competition, "'code' missing in competition"
        assert "name" in competition, "'name' missing in competition"

        for country in tournament["countries"]:
            assert "short_code" in country, "'short_code' missing in country"
            assert "code" in country, "'code' missing in country"
            assert "name" in country, "'name' missing in country"
            assert "official_name" in country, "'official_name' missing in country"
            assert "is_region" in country, "'is_region' missing in country"



def test_tc_06_no_featured_tournaments_returns_empty_list(base_url, valid_headers):
    association_key_with_no_tournaments = "a-ga6--ind-tnca"
    url = f"{base_url}{ENDPOINT.format(key=association_key_with_no_tournaments)}"

    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    json_data = response.json()
    
    assert "http_status_code" in json_data, "'http_status_code' missing in response"
    assert json_data["http_status_code"] == 200, f"Expected http_status_code 200, got {json_data['http_status_code']}"
    
    assert "data" in json_data, "'data' key missing in response"
    assert "tournaments" in json_data["data"], "'tournaments' key missing in data"
    
    tournaments = json_data["data"]["tournaments"]
    
    assert isinstance(tournaments, list), "'tournaments' should be a list"
    assert len(tournaments) == 0, f"Expected no featured tournaments, but found {len(tournaments)}"



def test_tc_07_graphql_rest_featured_tournaments_match(graphql_headers, valid_headers, base_url):
    
    GRAPHQL_PAYLOAD_FILE = "data/association/featured_tournaments_query.json"
    graphql_url = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    with open(GRAPHQL_PAYLOAD_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_payload["variables"] = {
        "associationKey": AssociationState.key}

    graphql_response = make_graphql_request(
        url=graphql_url,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )

    assert graphql_response.status_code == 200, f"Failed with status {graphql_response.status_code}, response: {graphql_response.text}"
    graphql_tournaments = graphql_response.json()["data"]["cricket_featured_tournaments"]["tournaments"]
    assert isinstance(graphql_tournaments, list)
    assert len(graphql_tournaments) > 0, "GraphQL response should contain tournaments"

    # REST 
    rest_url =f"{base_url}{ENDPOINT.format(key=AssociationState.key)}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200
    rest_tournaments = rest_response.json()["data"]["tournaments"]

    rest_dict = {item["key"]: item for item in rest_tournaments}


      #need to check  key, name, short_name, 
      # countries, start_date, gender, point_system, 
      # competition, association_key, metric_group, 
      # sport, is_date_confirmed, is_venue_confirmed, 
      # last_scheduled_match_date, and formats

    for gql_item in graphql_tournaments:
        key = gql_item["key"]
        assert key in rest_dict, f"Tournament {key} not found in REST"

        rest_item = rest_dict[key]

        assert gql_item["name"] == rest_item["name"], f"Name mismatch for {key}"
        assert gql_item["short_name"] == rest_item["short_name"], f"Short name mismatch for {key}"
        assert gql_item["start_date"] == rest_item["start_date"], f"Start date mismatch for {key}"
        assert gql_item["gender"].lower() == rest_item["gender"].lower(), f"Gender mismatch for {key}"
        # assert gql_item["point_system"].lower() == rest_item["point_system"].lower(), f"Point system mismatch for {key}"
        # "point_system": "NoPoints", in gql
        # "point_system": "no_points", in rest
        assert gql_item["association_key"] == rest_item["association_key"], f"Association key mismatch for {key}"
        assert gql_item["metric_group"] == rest_item["metric_group"], f"Metric group mismatch for {key}"
        assert gql_item["sport"].lower() == rest_item["sport"], f"Sport mismatch for {key}"
        assert gql_item["is_date_confirmed"] == rest_item["is_date_confirmed"], f"Date confirmed mismatch for {key}"
        assert gql_item["is_venue_confirmed"] == rest_item["is_venue_confirmed"], f"Venue confirmed mismatch for {key}"
        assert gql_item["last_scheduled_match_date"] == rest_item["last_scheduled_match_date"], f"Last match date mismatch for {key}"
        assert gql_item["formats"] == [f.upper() for f in rest_item["formats"]], f"Formats mismatch for {key}"

        # Competition
        gql_comp = gql_item["competition"]
        rest_comp = rest_item["competition"]
        assert gql_comp["key"] == rest_comp["key"], f"Competition key mismatch for {key}"
        assert gql_comp["code"] == rest_comp["code"], f"Competition code mismatch for {key}"
        assert gql_comp["name"] == rest_comp["name"], f"Competition name mismatch for {key}"

        # Countries 
        gql_countries = gql_item.get("countries", [])
        rest_countries = rest_item.get("countries", [])

        assert len(gql_countries) == len(rest_countries), f"Country count mismatch for {key}"

        for g_country, r_country in zip(gql_countries, rest_countries):
            assert g_country["short_code"] == r_country["short_code"], f"Country short_code mismatch in {key}"
            assert g_country["code"] == r_country["code"], f"Country code mismatch in {key}"
            assert g_country["name"] == r_country["name"], f"Country name mismatch in {key}"
            assert g_country["official_name"] == r_country["official_name"], f"Country official_name mismatch in {key}"
            assert g_country["is_region"] == r_country["is_region"], f"Country is_region mismatch in {key}"

    