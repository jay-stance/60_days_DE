import json
from confluent_kafka import Consumer, Producer

from configparser import ConfigParser
from argparse import ArgumentParser, FileType

# Parse the command line.
parser = ArgumentParser()
parser.add_argument('config_file', type=FileType('r'))
args = parser.parse_args()

# Parse the configuration.
consumer_config = ConfigParser()
consumer_config.read_file(args.config_file)
config = dict(consumer_config['default'])
config.update(consumer_config['consumer'])

consumer = Consumer(consumer_config)

producer_config = ConfigParser()
producer_config.read_file(args.config_file)
producer_config = dict(producer_config['default'])
producer_config.update(producer_config['producer'])

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