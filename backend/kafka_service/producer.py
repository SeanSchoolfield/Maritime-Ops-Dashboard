from kafka import KafkaProducer
import json
import os

if os.getenv("ENV") != "test":
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_message(topic, key, message):
    producer.send(topic, key=key, value=message)
    producer.flush()

'''if __name__ == "__main__":
    send_message("ship1", {"status": "Arrived at port"})
    send_message("ship2", {"status": "Departed for sea"})'''
