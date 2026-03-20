from confluent_kafka import Consumer
import json 
import psycopg2

# 1. Connect to the Database (External Sink)
db_conn = psycopg2.connect("dbname=iot_db user=admin password=secret")
cursor = db_conn.cursor()


def on_revoke(consumer, partitions):
    print("Kafka is taking my partition! Triggering emergency flush...")
    
    if len(valid_records) > 0:
        # 1. Save the data to the database
        cursor.executemany(upsert_query, valid_records)
        db_conn.commit()
        
        # 2. Tell Kafka we successfully processed this final batch
        # We find the very last message in our batch and commit its high-water mark
        last_msg = valid_records_raw_messages[-1] 
        consumer.commit(message=last_msg)
        
        # 3. Clear our memory
        valid_records.clear()
        print("Data saved and offset committed. Partition handed back safely.")

config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'group.id': 'thermostat_scaling_group', # <-- THIS IS THE MAGIC KEY
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['thermostat_readings'], on_revoke=on_revoke)


# The Micro-Batching Consumer Pattern
consumer.subscribe(['thermostat_readings'])

BATCH_SIZE = 500

try:
    while True:
        # 1. Use consume() to pull a list of up to 500 messages at once
        # It waits 1.0 second, OR until it hits 500 messages, whichever comes first.
        messages = consumer.consume(num_messages=BATCH_SIZE, timeout=1.0)
        
        if len(messages) == 0:
            continue

        valid_records = []
        
        # 2. Loop through the batch in Python memory (Super fast)
        for msg in messages:
            if msg.error():
                continue
            
            payload = json.loads(msg.value().decode('utf-8'))
            valid_records.append((
                payload.get('sensor_id'), 
                payload.get('temperature'), 
                payload.get('read_at')
            ))

        # 3. BULK INSERT to Postgres (1 network trip instead of 500!)
        upsert_query = """
            INSERT INTO thermostat_data (sensor_id, temperature, read_at)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        # executemany is highly optimized for bulk data
        cursor.executemany(upsert_query, valid_records)
        db_conn.commit()

        # 4. Commit the highest offset in the batch
        consumer.commit(messages[-1])
        print(f"✅ Bulk inserted {len(valid_records)} rows!")

except KeyboardInterrupt:
    pass