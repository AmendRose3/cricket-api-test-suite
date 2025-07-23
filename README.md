TEST SUITE/
├── assets/                         # Optional assets like images or documentation references
├── data/                          
│   └── auth_expected_data.py       # Contains static expected data for auth tests
├── shared/                         # Shared test utilities and data
├── tests/                          # All test files grouped by modules/features
│   ├── auth_tests.py               # Tests for authentication-related cases (TC-01 to TC-04)
│   ├── Association_List_Tests.py   # Tests for association list API, pagination, etc.
├── utils/                          
│   └── request_handler.py          # Wrapper for sending REST/GraphQL HTTP requests
├── conftest.py                     # Reusable pytest fixtures (e.g., headers, base_url)
├── report.html                     # HTML test execution report (auto-generated)
├── requirements.txt                # Python dependencies for running the test suite
└── README.md                       # Project overview, setup, and usage instructions

TEST CASES
https://docs.google.com/spreadsheets/d/1ZD_de5ntkz6oPYfoY0z1SDX0hbmvUSnoRdFaUSTkwwM/edit?usp=sharing
