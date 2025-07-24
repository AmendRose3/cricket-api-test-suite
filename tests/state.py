# tests/state.py

class RestAuthState:
    rzaccountkey: str = ""
    rztoken: str = ""
    rzapikey: str = ""
    user_key: str = ""
    admin_user_key: str = ""


class GraphQLState:
    graphql_token: str = ""
    graphql_account_key: str = ""
    graphql_api_key: str = ""
    graphql_user_key: str = ""
    graphql_admin_user_key: str = ""


class AssociationState:
    parent_key: str = "a-intern-test--icc-aJRI"
    child_key: str = "a-intern-test--asso-68q5"
    regional_key: str = "a-intern-test--cwi-mcgp"

    
class CountryState:
    code: str = "AUS"

