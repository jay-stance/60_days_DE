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