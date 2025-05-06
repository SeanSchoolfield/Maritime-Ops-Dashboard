from unittest.mock import patch, MagicMock
from backend.processors.gfw import fishing_api

@patch('backend.processors.gfw.fishing_api.KafkaProducer')
@patch('backend.processors.gfw.fishing_api.requests.post')
def test_fishing_api_process_success(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "fish123",
            "type": "fishing",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "position": {"lat": 0.0, "lon": 0.0},
            "distances": {"endDistanceFromPortKm": 1.0, "endDistanceFromShoreKm": 2.0},
            "fishing": {"averageSpeedKnots": 0},
            "vessel": {"name": "Fishy", "mmsi": "123456789"}
        }]
    }
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer


    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        fishing_api.process_fishing_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.fishing_api.KafkaProducer')
@patch('backend.processors.gfw.fishing_api.requests.post')
def test_fishing_api_empty_response(mock_post, mock_producer_cls):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"entries": []}

    mock_producer = MagicMock()
    mock_producer_cls.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        fishing_api.process_fishing_events()

    mock_post.assert_called_once()
    mock_producer.send.assert_not_called()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.fishing_api.KafkaProducer')
@patch('backend.processors.gfw.fishing_api.requests.post')
def test_fishing_api_kafka_send_error(mock_post, mock_producer_cls):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "entries": [{
            "id": "error-fish",
            "type": "fishing",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "position": {"lat": 0.0, "lon": 0.0},
            "distances": {"endDistanceFromPortKm": 1.0, "endDistanceFromShoreKm": 2.0},
            "fishing": {"averageSpeedKnots": 0},
            "vessel": {"name": "BrokenBoat", "mmsi": "fail-mmsi"}
        }]
    }

    mock_producer = MagicMock()
    mock_producer.send.side_effect = Exception("Kafka send error")
    mock_producer_cls.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        fishing_api.process_fishing_events()

    mock_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.fishing_api.KafkaProducer')
@patch('backend.processors.gfw.fishing_api.requests.post')
def test_fishing_api_bad_status(mock_post, mock_producer_cls):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "Internal Server Error"

    mock_producer = MagicMock()
    mock_producer_cls.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        with patch("sys.exit") as mock_exit:
            fishing_api.process_fishing_events()
            mock_exit.assert_called_once()
