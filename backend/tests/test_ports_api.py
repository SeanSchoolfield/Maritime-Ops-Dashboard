from unittest.mock import patch, MagicMock
from backend.processors.gfw import ports_api

@patch("backend.processors.gfw.ports_api.KafkaProducer")
@patch("backend.processors.gfw.ports_api.requests.post")
def test_ports_api_process_event(mock_post, mock_producer_cls):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "port1",
            "type": "port",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "vessel": {"name": "DockedOne", "ssvid": "123456789"}
        }]
    }
    mock_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_producer_cls.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        ports_api.process_ports_events()

    mock_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch("backend.processors.gfw.ports_api.requests.post")
def test_ports_api_empty_response(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": []}
    mock_post.return_value = mock_response

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        result = ports_api.requests.post("dummy", headers={}, json={})
        assert result.json() == {"entries": []}

@patch("backend.processors.gfw.ports_api.requests.post")
def test_ports_api_invalid_status_code(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        result = ports_api.requests.post("dummy", headers={}, json={})
        assert result.status_code == 500
