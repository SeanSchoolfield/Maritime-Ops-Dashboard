from kafka import KafkaProducer
import json

producer = None

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

def send_message(topic, key, value):
    global producer
    if producer is None:
        producer = get_kafka_producer()
    try:
        producer.send(topic, key=key, value=value)
        producer.flush()
    except Exception as e:
        print(f"[Kafka Producer] Error sending message: {e}")
