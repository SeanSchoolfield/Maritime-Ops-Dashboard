from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_message(key, message):
    producer.send('maritime-events', key=key, value=message)
    producer.flush()

if __name__ == "__main__":
    send_message("ship1", {"status": "Arrived at port"})
    send_message("ship2", {"status": "Departed for sea"})
