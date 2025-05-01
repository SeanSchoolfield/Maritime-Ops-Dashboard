from unittest.mock import patch, MagicMock
from backend.processors.gfw import transponder_api

@patch("backend.processors.gfw.transponder_api.KafkaProducer")
@patch("backend.processors.gfw.transponder_api.requests.post")
def test_transponder_api_success(mock_post, mock_kafka_producer):
    # Mock API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "trans1",
            "type": "gap",
            "start": "2025-01-01T00:00:00Z",
            "end": "2025-12-31T00:00:00Z",
            "vessel": {"name": "GhostShip", "ssvid": "999999999"}
        }]
    }
    mock_post.return_value = mock_response

    # Mock Kafka producer
    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    # Run the function
    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        transponder_api.process_transponder_events()

    # Assertions
    mock_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch("backend.processors.gfw.transponder_api.KafkaProducer")
@patch("backend.processors.gfw.transponder_api.requests.post")
def test_transponder_api_empty_events(mock_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": []}
    mock_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        transponder_api.process_transponder_events()

    mock_post.assert_called_once()
    mock_producer.send.assert_not_called()
    mock_producer.flush.assert_called_once()

@patch("backend.processors.gfw.transponder_api.KafkaProducer")
@patch("backend.processors.gfw.transponder_api.requests.post")
def test_transponder_api_error_response(mock_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Server Error"
    mock_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        with patch("sys.exit") as mock_exit:
            transponder_api.process_transponder_events()
            mock_exit.assert_called_once()
