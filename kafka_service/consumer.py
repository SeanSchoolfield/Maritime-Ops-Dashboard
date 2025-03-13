from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'maritime-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("Listening for events...")
for message in consumer:
    print(f"Timestamp: {message.timestamp}, Key: {message.key}, Value: {message.value}")
