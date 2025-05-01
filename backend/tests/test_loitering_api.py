from unittest.mock import patch, MagicMock
from backend.processors.gfw import loitering_api

@patch('backend.processors.gfw.loitering_api.KafkaProducer')
@patch('backend.processors.gfw.loitering_api.requests.post')
def test_loitering_api_process(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [
            {
                "id": "event123",
                "type": "loitering",
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-12-31T00:00:00Z",
                "position": {"lat": 0.0, "lon": 0.0},
                "distances": {
                    "endDistanceFromPortKm": 1.0,
                    "endDistanceFromShoreKm": 2.0
                },
                "loitering": {"averageSpeedKnots": 0},
                "vessel": {"name": "TestVessel", "mmsi": "123456789"}
            }
        ]
    }
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        loitering_api.producer = mock_producer
        loitering_api.process_loitering_events()

    # Assertions
    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.loitering_api.KafkaProducer')
@patch('backend.processors.gfw.loitering_api.requests.post')
def test_loitering_api_empty_response(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": []}
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        loitering_api.producer = mock_producer
        loitering_api.process_loitering_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_not_called()
    mock_producer.flush.assert_called_once()



@patch('backend.processors.gfw.loitering_api.KafkaProducer')
@patch('backend.processors.gfw.loitering_api.requests.post')
def test_loitering_api_kafka_send_error(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "event-error",
            "type": "loitering",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "position": {"lat": 0.0, "lon": 0.0},
            "distances": {"endDistanceFromPortKm": 1.0, "endDistanceFromShoreKm": 2.0},
            "loitering": {"averageSpeedKnots": 0},
            "vessel": {"name": "FailVessel", "mmsi": "987654321"}
        }]
    }
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_producer.send.side_effect = Exception("Kafka send failed")
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        loitering_api.producer = mock_producer
        loitering_api.process_loitering_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()


@patch('backend.processors.gfw.loitering_api.KafkaProducer')
@patch('backend.processors.gfw.loitering_api.requests.post')
def test_loitering_api_missing_vessel(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "event-no-vessel",
            "type": "loitering",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "position": {"lat": 0.0, "lon": 0.0},
            "distances": {"endDistanceFromPortKm": 1.0, "endDistanceFromShoreKm": 2.0},
            "loitering": {"averageSpeedKnots": 0}
        }]
    }
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        loitering_api.producer = mock_producer
        loitering_api.process_loitering_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()


@patch('backend.processors.gfw.loitering_api.KafkaProducer')
@patch('backend.processors.gfw.loitering_api.requests.post')
def test_loitering_api_limited_movement(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "event-speed",
            "type": "loitering",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "position": {"lat": 0.0, "lon": 0.0},
            "distances": {"endDistanceFromPortKm": 1.0, "endDistanceFromShoreKm": 2.0},
            "loitering": {"averageSpeedKnots": 5},
            "vessel": {"name": "Speedy", "mmsi": "321654987"}
        }]
    }
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        loitering_api.producer = mock_producer
        loitering_api.process_loitering_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

