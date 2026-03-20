import time
import json
import random
from confluent_kafka import Producer

from confluent_kafka import Producer

# The High-Throughput, Low-Cost Config
config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT:9092',
    'acks': 'all',
    
    # --- BATCHING & COMPRESSION ---
    'linger.ms': 20,          # Wait artificially for 20 milliseconds to build a batch
    'batch.size': 32768,      # ...OR until the batch hits 32KB, whichever comes first
    'compression.type': 'snappy', # Compress the entire batch before sending
    
    # 2. THE MAGIC LINE
    'enable.idempotence': True
}

producer = Producer(config)

# Your while True loop stays EXACTLY the same. 
# You keep calling producer.produce() as fast as you can.
# The Producer will trap the messages in memory, compress them, 
# and send them in massive chunks every 20 milliseconds.



def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Failed to deliver message: {err}")
    # We remove the "Success" print statement in real-time pipelines 
    # because printing 10,000 times a second will crash your terminal!


print("Starting real-time sensor stream... (Press Ctrl+C to stop)")

try:
    while True:
        # 1. Generate the real-time data
        sensor_data = {
            "sensor_id": 42,
            "temp": round(random.uniform(20.0, 30.0), 2)
        }
        
        # 2. Fire the message into the background thread
        producer.produce(
            topic='thermostat_readings',
            key=str(sensor_data['sensor_id']),
            value=json.dumps(sensor_data),
            on_delivery=delivery_report
        )
        
        # 3. The Housekeeping! 
        # Instantly clears out any receipts sitting in memory so it doesn't overflow.
        producer.poll(0)
        
        # Simulate data arriving every 10 milliseconds
        time.sleep(0.01) 

except KeyboardInterrupt:
    print("\nStopping stream...")

finally:
    # 4. The Safety Net
    # If you hit Ctrl+C, there might be 50 messages still in the background thread 
    # waiting to go out. flush() blocks the script from dying until they are sent.
    print("Flushing remaining messages to Kafka...")
    producer.flush()
    print("Pipeline shut down safely.")