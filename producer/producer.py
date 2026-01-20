import os
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092")
topic = os.getenv("TOPIC_NAME", "events_topic")
counter_file = "/producer-data/producer_count.txt"

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers.split(","),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def load_counter():
    try:
        with open(counter_file, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_counter(c):
    with open(counter_file, "w") as f:
        f.write(str(c))

count = load_counter()

event_types = ["click", "view", "purchase"]

print(f"Starting producer, sending to {bootstrap_servers}, topic={topic}")
while True:
    event = {
        "id": count,
        "event_type": random.choice(event_types),
        "timestamp": datetime.utcnow().isoformat(),
    }
    producer.send(topic, event)
    count += 1
    if count % 100 == 0:
        save_counter(count)
        print(f"Produced events: {count}")
    time.sleep(0.1)