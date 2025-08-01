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

ENDPOINT = "news-aggregation/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_news_aggregation_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT.format(match_key=MatchState.key)}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    news_data = response.json()


    assert "data" in news_data, "'data' key missing in response"
    assert "news" in news_data["data"], "'news' key missing in 'data'"
    assert isinstance(news_data["data"]["news"], list), "'news' should be a list"

  
    for item in news_data["data"]["news"]:
        assert "title" in item and isinstance(item["title"], str), "Missing or invalid 'title'"
        assert "description" in item and isinstance(item["description"], str), "Missing or invalid 'description'"
        assert "description_text" in item and isinstance(item["description_text"], str), "Missing or invalid 'description_text'"
        assert "image_url" in item and isinstance(item["image_url"], str), "Missing or invalid 'image_url'"
        assert "link" in item and isinstance(item["link"], str), "Missing or invalid 'link'"
        assert "provider" in item and isinstance(item["provider"], dict), "Missing or invalid 'provider'"
        assert "name" in item["provider"], "Missing 'provider.name'"
        assert "url" in item["provider"], "Missing 'provider.url'"
        assert "updated" in item and isinstance(item["updated"], str), "Missing or invalid 'updated'"


def test_tc_04_rest_graphql_validate(base_url, valid_headers, graphql_headers):

    GRAPHQL_URL = "https://ants-api.sports.dev.roanuz.com/v5/gql/"

    GRAPHQL_POINTS_QUERY_FILE = "data/new/news_query.json"

    with open(GRAPHQL_POINTS_QUERY_FILE, "r") as f:
        gql_payload = json.load(f)

    gql_response = make_graphql_request(
        url=GRAPHQL_URL,
        headers=graphql_headers,
        query=gql_payload["query"],
        variables=gql_payload["variables"],
        operation_name=gql_payload["operationName"]
    )
    assert gql_response.status_code == 200, f"GraphQL error: {gql_response.text}"
    gql_data = gql_response.json()["data"]["cricket_news_aggregation"]["news"]

    rest_url = f"{base_url}{ENDPOINT}"
    rest_response = send_get_request(rest_url, headers=valid_headers)
    assert rest_response.status_code == 200, f"REST API failed with {rest_response.status_code}"
    rest_data = rest_response.json()["data"]["news"]
    assert len(gql_data) == len(rest_data),"Number of news differs"

    for i in range(len(gql_data)):
        assert gql_data[i]["title"] == rest_data[i]["title"],f"difference in the title at {i}"
