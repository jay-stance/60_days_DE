import json
from confluent_kafka import Consumer, Producer

# 1. Setup the Consumer (Manual Commits Enabled)
consumer_config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'YOUR_API_KEY',
    'sasl.password': 'YOUR_API_SECRET',
    'group.id': 'senior_pipeline_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # WE CONTROL THE COMMITS NOW
}
consumer = Consumer(consumer_config)

# 2. Setup the Producer (For the DLQ)
producer_config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'YOUR_API_KEY',
    'sasl.password': 'YOUR_API_SECRET'
}
dlq_producer = Producer(producer_config)

MAIN_TOPIC = 'thermostat_readings'
DLQ_TOPIC = 'thermostat_readings_dlq'

consumer.subscribe([MAIN_TOPIC])

print("Listening for data... (Press Ctrl+C to stop)")

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
        elif msg.error():
            print(f"Kafka Error: {msg.error()}")
            continue

        # --- THE DLQ PATTERN STARTS HERE ---
        raw_value = msg.value().decode('utf-8')

        try:
            # 3. Attempt to process the message properly
            payload = json.loads(raw_value)
            
            # (Your database insert logic would go here)
            print(f"✅ SUCCESS: Sensor {payload.get('sensor_id')} read {payload.get('temperature')}°C")

            # 4. It worked! Commit the offset to move forward.
            consumer.commit(msg)

        except json.JSONDecodeError:
            # 5. POISON PILL CAUGHT! Do NOT let the script crash.
            print(f"☠️ POISON PILL DETECTED: Cannot parse JSON -> {raw_value}")
            
            # 6. Route the bad message to the quarantine topic
            dlq_producer.produce(
                topic=DLQ_TOPIC, 
                key=msg.key(), 
                value=msg.value()
            )
            dlq_producer.flush() # Ensure it sends immediately
            
            print(f"📦 Sent bad message to {DLQ_TOPIC}")

            # 7. CRITICAL: Commit the offset anyway so we don't get stuck in a loop!
            consumer.commit(msg)

except KeyboardInterrupt:
    print("Shutting down gracefully...")
finally:
    consumer.close()