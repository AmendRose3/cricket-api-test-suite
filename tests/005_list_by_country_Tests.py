import pytest,requests,json
from utils.request_handler import send_get_request,make_graphql_request
from state import CountryState
from utils.auth import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)
country_code = CountryState.code
ENDPOINT = "association/list-by-country/{country_code}/"

def test_tc_01_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_tc_02_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_tc_03_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_tc_04_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)

