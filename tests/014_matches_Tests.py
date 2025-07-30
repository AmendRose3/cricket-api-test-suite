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

ENDPOINT = "match/{match_key}/"

def test_valid_token_authentication(base_url, valid_headers):
    print(valid_headers)
    print(ENDPOINT)
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

def test_tc_05_featured_matches_detail_structure(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    json_data = response.json()