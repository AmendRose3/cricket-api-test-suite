from data.rest.auth_expected_data import EXPECTED_INVALID_TOKEN_ERROR
from utils.request_handler import send_get_request

def run_valid_token_authentication(endpoint, base_url, valid_headers):
    url = f"{base_url}{endpoint}"
    res = send_get_request(url, headers=valid_headers)
    assert res.status_code == 200
    json_data = res.json()
    assert "data" in json_data


def run_invalid_token(endpoint, base_url, invalid_headers):
    url = f"{base_url}{endpoint}"
    res = send_get_request(url, headers=invalid_headers)

    assert res.status_code == 401
    json_data = res.json()
    assert json_data["error"]["code"] == EXPECTED_INVALID_TOKEN_ERROR["code"]
    assert json_data["error"]["http_status_code"] == EXPECTED_INVALID_TOKEN_ERROR["http_status_code"]
    assert json_data["error"]["msg"] == EXPECTED_INVALID_TOKEN_ERROR["msg"]


def run_missing_token(endpoint, base_url, no_token_headers):
    url = f"{base_url}{endpoint}"
    res = send_get_request(url, headers=no_token_headers)

    assert res.status_code == 401
    json_data = res.json()
    assert json_data["error"]["code"] == EXPECTED_INVALID_TOKEN_ERROR["code"]
    assert json_data["error"]["http_status_code"] == EXPECTED_INVALID_TOKEN_ERROR["http_status_code"]
    assert json_data["error"]["msg"] == EXPECTED_INVALID_TOKEN_ERROR["msg"]


def run_empty_token(endpoint, base_url, empty_token_headers):
    url = f"{base_url}{endpoint}"
    res = send_get_request(url, headers=empty_token_headers)

    assert res.status_code == 401
    json_data = res.json()
    assert json_data["error"]["code"] == EXPECTED_INVALID_TOKEN_ERROR["code"]
    assert json_data["error"]["http_status_code"] == EXPECTED_INVALID_TOKEN_ERROR["http_status_code"]
    assert json_data["error"]["msg"] == EXPECTED_INVALID_TOKEN_ERROR["msg"]

