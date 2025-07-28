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
    key: str="a-intern-test--bcci-OFJF"
    parent_key: str = "a-intern-test--icc-aJRI"
    child_key: str = "a-intern-test--asso-68q5"
    regional_key: str = "a-intern-test--cwi-mcgp"

    
class CountryState:
    code: str = "AUS"

class StadiumState:
    key: str='a-intern-test--chep-yvDg'

class TournamentState:
    key: str='a-intern-test--cricket--samp-xu3D--tour-ta-6K43-tb-W9Df-T20--2025-hG3R'


