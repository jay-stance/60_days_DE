import json
import psycopg2
from confluent_kafka import Consumer

# 1. Connect to the Database (External Sink)
db_conn = psycopg2.connect("dbname=iot_db user=admin password=secret")
cursor = db_conn.cursor()

# 2. Setup the Consumer (Manual Commits)
consumer = Consumer({
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'group.id': 'idempotent_db_writer',
    'enable.auto.commit': False
})
consumer.subscribe(['thermostat_readings'])

print("Listening and writing to Postgres...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        payload = json.loads(msg.value().decode('utf-8'))
        
        sensor = payload.get('sensor_id')
        temp = payload.get('temperature')
        timestamp = payload.get('read_at')

        # --- THE IDEMPOTENT DB PATTERN STARTS HERE ---

        # 3. The "UPSERT" SQL Query
        # We assume the database table has a UNIQUE constraint on (sensor_id, read_at)
        upsert_query = """
            INSERT INTO thermostat_data (sensor_id, temperature, read_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (sensor_id, read_at) 
            DO UPDATE SET temperature = EXCLUDED.temperature;
        """
        
        try:
            # 4. Execute the DB write
            cursor.execute(upsert_query, (sensor, temp, timestamp))
            db_conn.commit()  # Commit the database transaction
            
            # 5. Only if the DB succeeds, commit the Kafka offset!
            consumer.commit(msg)
            print(f"✅ Safely saved/updated Sensor {sensor}")

        except Exception as e:
            # If the database goes down, we DO NOT commit the Kafka offset.
            # The script will just retry this message on the next loop.
            db_conn.rollback()
            print(f"Database error: {e}")

except KeyboardInterrupt:
    pass
finally:
    cursor.close()
    db_conn.close()
    consumer.close()