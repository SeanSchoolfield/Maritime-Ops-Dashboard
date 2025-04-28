from unittest.mock import patch, MagicMock
import backend.kafka_service.producer as producer_module

@patch('backend.kafka_service.producer.get_kafka_producer')
def test_send_vessel_data(mock_get_producer):
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    topic = "GFW"
    key = "123456789"
    value = {"mmsi": "123456789", "status": "ACTIVE"}

    producer_module.producer = None
    producer_module.send_message(topic, key, value)

    mock_producer.send.assert_called_with(topic, key=key, value=value)
    mock_producer.flush.assert_called_once()

def test_lazy_initialization():
    producer_module.producer = None

    with patch('backend.kafka_service.producer.KafkaProducer') as mock_kafka_producer:
        mock_instance = MagicMock()
        mock_kafka_producer.return_value = mock_instance

        producer_module.send_message("GFW", "test_key", {"data": 123})
        mock_kafka_producer.assert_called_once()
        mock_instance.send.assert_called_once_with("GFW", key="test_key", value={"data": 123})

@patch('backend.kafka_service.producer.get_kafka_producer')
def test_send_message_serialization_error(mock_get_producer, capsys):
    mock_producer = MagicMock()
    mock_producer.send.side_effect = Exception("Serialization failed")
    mock_get_producer.return_value = mock_producer

    producer_module.producer = None
    producer_module.send_message("GFW", "test_key", {"data": set()})

    captured = capsys.readouterr()
    assert "[Kafka Producer] Error sending message" in captured.out

@patch('backend.kafka_service.producer.get_kafka_producer')
def test_send_correct_topic(mock_get_producer):
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    producer_module.producer = None
    producer_module.send_message("GFW", "vessel123", {"foo": "bar"})
    mock_producer.send.assert_called_with("GFW", key="vessel123", value={"foo": "bar"})
