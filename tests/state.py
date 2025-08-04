# tests/state.py

# class RestAuthState:
#     rzaccountkey: str = ""
#     rztoken: str = ""
#     rzapikey: str = ""
#     user_key: str = ""
#     admin_user_key: str = ""


# class GraphQLState:
#     graphql_token: str = ""
#     graphql_account_key: str = ""
#     graphql_api_key: str = ""
#     graphql_user_key: str = ""
#     graphql_admin_user_key: str = ""


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
    key: str='a-intern-test--cricket--isa2j-Srxj--is2j-GrV8--2025-NmJf'
    team_key: str='a-intern-test--cricket--csk-a43S'

class MatchState:
    key: str='a-intern-test--cricket--qo1950156409505226755'
    over_key: str='b_1_2'

