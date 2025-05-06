from unittest.mock import patch, MagicMock
from backend.processors.gfw import updater_api

def build_expected_url(mmsi):
    return (
        f"https://gateway.api.globalfishingwatch.org/v3/vessels/search"
        f"?query={mmsi}&datasets[0]=public-global-vessel-identity:latest"
        f"&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
    )

@patch("backend.processors.gfw.updater_api.requests.get")
@patch("backend.processors.gfw.updater_api.DBOperator")
def test_run_update(mock_db_operator_class, mock_requests_get):
    mock_db = MagicMock()
    mock_db.query.return_value = [
        {"mmsi": "123456789"},
        {"mmsi": "987654321"}
    ]
    mock_db_operator_class.return_value = mock_db
    updater_api.operator = mock_db

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": [{"name": "Mock Vessel"}]}
    mock_requests_get.return_value = mock_response

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        updater_api.headers = {"Authorization": "Bearer fake-token"}
        updater_api.run_update()

    expected_urls = [
        build_expected_url("123456789"),
        build_expected_url("987654321"),
    ]

    actual_calls = mock_requests_get.call_args_list
    assert len(actual_calls) == 2

    for call_args, expected_url in zip(actual_calls, expected_urls):
        args, kwargs = call_args
        assert args[0] == expected_url
        assert kwargs["headers"] == {"Authorization": "Bearer fake-token"}

    mock_db.query.assert_called_once()

@patch("backend.processors.gfw.updater_api.requests.get")
@patch("backend.processors.gfw.updater_api.DBOperator")
def test_run_update_with_no_vessels(mock_db_operator_class, mock_requests_get):
    mock_db = MagicMock()
    mock_db.query.return_value = []
    mock_db_operator_class.return_value = mock_db
    updater_api.operator = mock_db

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        updater_api.headers = {"Authorization": "Bearer fake-token"}
        updater_api.run_update()

    mock_requests_get.assert_not_called()
    mock_db.query.assert_called_once()

@patch("backend.processors.gfw.updater_api.requests.get")
@patch("backend.processors.gfw.updater_api.DBOperator")
def test_run_update_with_failed_api_response(mock_db_operator_class, mock_requests_get):
    mock_db = MagicMock()
    mock_db.query.return_value = [{"mmsi": "123456789"}]
    mock_db_operator_class.return_value = mock_db
    updater_api.operator = mock_db

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}
    mock_requests_get.return_value = mock_response

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        updater_api.headers = {"Authorization": "Bearer fake-token"}
        updater_api.run_update()

    assert mock_requests_get.call_count == 1

@patch("backend.processors.gfw.updater_api.requests.get")
@patch("backend.processors.gfw.updater_api.DBOperator")
def test_run_update_with_missing_mmsi(mock_db_operator_class, mock_requests_get):
    mock_db = MagicMock()
    mock_db.query.return_value = [{"name": "Unnamed Vessel"}]
    mock_db_operator_class.return_value = mock_db
    updater_api.operator = mock_db

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        updater_api.headers = {"Authorization": "Bearer fake-token"}
        updater_api.run_update()

    mock_requests_get.assert_not_called()

@patch("backend.processors.gfw.updater_api.requests.get")
@patch("backend.processors.gfw.updater_api.DBOperator")
def test_run_update_with_missing_token(mock_db_operator_class, mock_requests_get):
    mock_db = MagicMock()
    mock_db.query.return_value = [{"mmsi": "123456789"}]
    mock_db_operator_class.return_value = mock_db
    updater_api.operator = mock_db

    with patch.dict("os.environ", {}, clear=True):
        with patch("sys.exit") as mock_exit:
            updater_api.GFW_TOKEN = None
            updater_api.headers = {}
            updater_api.run_update()
            mock_exit.assert_called_once()
