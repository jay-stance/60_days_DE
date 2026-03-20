from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'pkc-YOUR-ENDPOINT:9092', 'acks': 'all'})

# Scenario A: We NEED strict ordering for this specific sensor
sensor_data = {"sensor_id": 42, "temp": 100}

producer.produce(
    topic='thermostat_readings',
    # 1. We pass the sensor_id as a string to the 'key' argument.
    # Kafka hashes this string and assigns it to a deterministic partition.
    key=str(sensor_data['sensor_id']), 
    value=json.dumps(sensor_data)
)

# Scenario B: We DO NOT care about order, just balance the load!
website_click = {"user": "anonymous", "action": "button_click"}

producer.produce(
    topic='website_metrics',
    # 2. We explicitly pass None (or just omit the argument).
    # Kafka uses Sticky Round-Robin to distribute the batches evenly.
    key=None, 
    value=json.dumps(website_click)
)

producer.flush()