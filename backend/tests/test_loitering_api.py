from unittest.mock import patch, MagicMock
from backend.processors.gfw import loitering_api

@patch('backend.processors.gfw.loitering_api.get_kafka_producer')
@patch('backend.processors.gfw.loitering_api.requests.get')
def test_loitering_api_process(mock_requests_get, mock_get_producer):
    # Mock API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "events": [
            {"mmsi": "123456789", "event": "LOITERING"}
        ]
    }
    mock_requests_get.return_value = mock_response

    # Mock Kafka producer
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    # Call the function you'd have in loitering_api to process data
    loitering_api.process_loitering_events()

    mock_requests_get.assert_called()
    mock_producer.send.assert_called()
    mock_producer.flush.assert_called_once()
