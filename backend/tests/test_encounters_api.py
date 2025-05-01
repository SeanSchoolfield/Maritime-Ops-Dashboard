from unittest.mock import patch, MagicMock
from backend.processors.gfw import encounters_api

@patch('backend.processors.gfw.encounters_api.KafkaProducer')
@patch('backend.processors.gfw.encounters_api.requests.post')
def test_encounters_api_process_success(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "encounter123",
            "type": "encounter",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "encounter": {
                "medianDistanceKilometers": 1.23,
                "potentialRisk": True,
                "vessel": {"name": "Guesty", "ssvid": "987654321"}
            },
            "vessel": {"name": "Hosty", "ssvid": "123456789"}
        }]
    }
    mock_requests_post.return_value = mock_response
    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        encounters_api.process_encounter_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.encounters_api.KafkaProducer')
@patch('backend.processors.gfw.encounters_api.requests.post')
def test_encounters_api_empty_response(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": []}
    mock_requests_post.return_value = mock_response

    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        encounters_api.process_encounter_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_not_called()
    mock_producer.flush.assert_called_once()

@patch('backend.processors.gfw.encounters_api.KafkaProducer')
@patch('backend.processors.gfw.encounters_api.requests.post')
def test_encounters_api_missing_vessel_info(mock_requests_post, mock_kafka_producer):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "entries": [{
            "id": "encounter456",
            "type": "encounter",
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T00:00:00Z",
            "encounter": {
                "medianDistanceKilometers": 2.0,
                "potentialRisk": False,
                "vessel": {}
            },
            "vessel": {}
        }]
    }
    mock_requests_post.return_value = mock_response
    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    with patch.dict("os.environ", {"TOKEN": "fake-token"}):
        encounters_api.process_encounter_events()

    mock_requests_post.assert_called_once()
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()
