from confluent_kafka import Consumer

# 1. The Critical Setting: group.id
# Every instance of this script MUST have the exact same group ID.
config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'group.id': 'thermostat_scaling_group', # <-- THIS IS THE MAGIC KEY
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['thermostat_readings'])

print("Worker started! Waiting for Kafka to assign a partition...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue
            
        # Do your heavy processing here...
        print(f"Processed by Worker: {msg.value().decode('utf-8')}")
        
except KeyboardInterrupt:
    pass
finally:
    consumer.close()