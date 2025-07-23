import pytest
import requests
from utils.request_handler import send_get_request,send_post_request,make_graphql_request
from data.rest.auth_expected_data import EXPECTED_INVALID_TOKEN_ERROR,PARENT_ASSOCIATION_KEY,CHILD_ASSOCIATION_KEY,REGIONAL_ASSOCIATION_KEY
from shared.auth_tests import (
    run_valid_token_authentication,
    run_invalid_token,
    run_missing_token,
    run_empty_token
)

ENDPOINT = "association/list/"

def test_valid_token_authentication(base_url, valid_headers):
    run_valid_token_authentication(ENDPOINT, base_url, valid_headers)

def test_invalid_token(base_url, invalid_headers):
    run_invalid_token(ENDPOINT, base_url, invalid_headers)

def test_missing_token(base_url, no_token_headers):
    run_missing_token(ENDPOINT, base_url, no_token_headers)

def test_empty_token(base_url, empty_token_headers):
    run_empty_token(ENDPOINT, base_url, empty_token_headers)


def test_tc_05_resource_not_found(valid_headers, base_url):
    invalid_url = f"{base_url}association/invalid-endpoint/"
    res = send_get_request(invalid_url, headers=valid_headers)

    assert res.status_code == 404
    assert res.text.strip() == "404: Not Found"


def test_tc_06_get_association_list_valid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_data = response.json()

    assert json_data["http_status_code"] == 200
    assert "data" in json_data
    assert "associations" in json_data["data"]
    assert isinstance(json_data["data"]["associations"], list)


def test_tc_07_post_association_list_invalid(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_post_request(url, headers=valid_headers) 

    assert response.status_code == 405, f"Expected 405, got {response.status_code}"
    assert "Method Not Allowed" in response.text


def test_tc_08_cache_object_present(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    json_data = response.json()

    assert response.status_code == 200
    assert "cache" in json_data, "Response missing 'cache' key"
    assert isinstance(json_data["cache"], dict), "Cache should be a dictionary"
    assert "key" in json_data["cache"], "'cache' missing 'key'"
    assert "expires" in json_data["cache"], "'cache' missing 'expires'"

def test_tc_09_required_fields_in_each_association(base_url, valid_headers):
    url = f"{base_url}{ENDPOINT}"
    response = send_get_request(url, headers=valid_headers)
    json_data = response.json()

    assert response.status_code == 200
    associations = json_data.get("data", {}).get("associations", [])

    for idx, association in enumerate(associations):
        assert "key" in association, f"Missing 'key' in association at index {idx}"
        assert "code" in association, f"Missing 'code' in association at index {idx}"
        assert "name" in association, f"Missing 'name' in association at index {idx}"

# The ICC does not belong to any country

def test_tc_10_icc_association_structure(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT}"
    res = requests.get(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    associations = data["data"]["associations"]

    icc_entry = next((a for a in associations if a["key"] == PARENT_ASSOCIATION_KEY), None)
    assert icc_entry is not None, f"ICC association with key {PARENT_ASSOCIATION_KEY} not found"

    assert icc_entry["code"] == "ICC"
    assert icc_entry["name"] == "International Cricket Council"
    assert icc_entry["country"]["name"] is None
    assert icc_entry["parent"] is None

# The international cricketing teams have their own governing associations. Examples for such associations include the BCCI, ECB etc. 
# The info provided for such Associations include a country object.

def test_tc_11_international_association_structure(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT}"
    res = requests.get(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    associations = data["data"]["associations"]

    entry = next((a for a in associations if a["key"] == CHILD_ASSOCIATION_KEY), None)
    assert entry is not None, f"child association with key {CHILD_ASSOCIATION_KEY} not found"

    assert entry["parent"] is not None
    assert entry["country"]["name"] is not None


#The West Indies Cricket Board does not represent a country

def test_tc_12_regional_association_structure(valid_headers, base_url):
    url = f"{base_url}{ENDPOINT}"
    res = requests.get(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    associations = data["data"]["associations"]

    entry = next((a for a in associations if a["key"] == REGIONAL_ASSOCIATION_KEY), None)
    assert entry is not None, f"child association with key {REGIONAL_ASSOCIATION_KEY} not found"

    assert entry["parent"] is None
    assert entry["country"] is not None
    assert entry["country"]["is_region"] is True



def test_tc_12_negetive_page_number(valid_headers, base_url):
    PAGE = "-100/"
    url = f"{base_url}{ENDPOINT}{PAGE}"
    res = requests.get(url, headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    print("Previous Page:", data["data"]["previous_page_key"])
    print("Next Page:", data["data"]["next_page_key"])

    assert data["data"]["previous_page_key"] is None
    assert data["data"]["next_page_key"] is None





def test_tc_12_zero_page_number(valid_headers, base_url):
    PAGE= "0/"
    url = f"{base_url}{ENDPOINT}{PAGE}"
    res = requests.get(url,headers=valid_headers)
    assert res.status_code == 200

    data = res.json()
    assert data["data"]["previous_page_key"] is None
    assert data["data"]["next_page_key"] is None



def test_tc_12_graphql_matches_rest(valid_headers, graphql_headers, base_url, graphql_url):
    print("Hello")
    rest_url = f"{base_url}{ENDPOINT}"
    rest_res = requests.get(rest_url, headers=valid_headers)
    assert rest_res.status_code == 200

    rest_data = rest_res.json()["data"]["associations"]
    rest_entry = next((a for a in rest_data if a["key"] == CHILD_ASSOCIATION_KEY), None)
    assert rest_entry is not None, f"Association with key {CHILD_ASSOCIATION_KEY} not found in REST"

    graphql_query = """
    query AssociationReadQuery($resource: AssociationInput!, $withHistory: Boolean) {
      sports_association_read(resource: $resource, with_history: $withHistory) {
        item {
          resource {
            key
            _hashkey
          }
          association {
            code
            name
            region {
              _hashkey
            }
            parent {
              _hashkey
            }
          }
        }
      }
    }
    """
    variables = {
        "resource": {"_hashkey": CHILD_ASSOCIATION_KEY},
        "withHistory": True
    }

    graphql_res = make_graphql_request(graphql_url, graphql_headers, graphql_query, variables, "AssociationReadQuery")
    assert graphql_res is not None
    assert graphql_res.status_code == 200
    graphql_data = graphql_res.json()["data"]["sports_association_read"]["item"]
    print("GraphQL Response Body:", graphql_data)
    print("RestAPI body :",rest_entry)


    gql_association = graphql_data["association"]

    print(graphql_data["resource"])
    assert graphql_data["resource"]["_hashkey"] == rest_entry["key"]
    assert gql_association["code"] == rest_entry["code"]
    assert gql_association["name"] == rest_entry["name"]
    assert gql_association["parent"]["_hashkey"] in rest_entry["parent"], "Parent mismatch"






