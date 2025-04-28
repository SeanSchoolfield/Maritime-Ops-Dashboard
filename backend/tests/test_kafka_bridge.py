from unittest.mock import patch, MagicMock
from backend.kafka_service.producer import send_message

@patch('backend.kafka_service.producer.KafkaProducer')
def test_send_message(mock_producer):
    producer_instance = mock_producer.return_value
    send_message("test-key", {"msg": "hello"})

    producer_instance.send.assert_called_once_with(
        'maritime-events',
        key='test-key',
        value={"msg": "hello"}
    )
    producer_instance.flush.assert_called_once()
