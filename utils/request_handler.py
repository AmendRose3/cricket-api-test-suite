import requests

#RestAPI

def send_get_request(url, headers):
    return requests.get(url, headers=headers)

def send_post_request(url, headers, payload=None):
    return requests.post(url, headers=headers, json=payload)



# payload=None to send_post_request() to support sending a JSON body for GraphQL or POST-based REST endpoints


#GraphQL

def make_graphql_request(url, headers, query, variables=None, operation_name=None):
    payload = {
        "query": query,
        "variables": variables or {},
        "operationName": operation_name,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response
