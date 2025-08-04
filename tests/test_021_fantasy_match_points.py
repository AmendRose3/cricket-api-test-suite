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

ENDPOINT = "fantasy-match-points/{match_key}/"

# def test_valid_token_authentication(base_url, valid_headers):
#     print(valid_headers)
#     run_valid_token_authentication(ENDPOINT.format(match_key=MatchState.key), base_url, valid_headers)

# def test_invalid_token(base_url, invalid_headers):
#     run_invalid_token(ENDPOINT.format(match_key=MatchState.key), base_url, invalid_headers)

# def test_missing_token(base_url, no_token_headers):
#     run_missing_token(ENDPOINT.format(match_key=MatchState.key), base_url, no_token_headers)

# def test_empty_token(base_url, empty_token_headers):
#     run_empty_token(ENDPOINT.format(match_key=MatchState.key), base_url, empty_token_headers)

