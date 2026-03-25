from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

# 1. Connect to the Schema Registry
sr_config = {
    'url': 'https://psrc-YOUR-ENDPOINT.confluent.cloud',
    'basic.auth.user.info': 'SR_API_KEY:SR_API_SECRET'
}
schema_registry_client = SchemaRegistryClient(sr_config)

# 2. Create the Deserializer (It will fetch schemas automatically)
avro_deserializer = AvroDeserializer(schema_registry_client)

# 3. Configure the Deserializing Consumer
consumer_config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'KAFKA_API_KEY',
    'sasl.password': 'KAFKA_API_SECRET',
    'group.id': 'senior_avro_group',
    'auto.offset.reset': 'earliest',
    # --- THE TRANSLATOR ---
    'value.deserializer': avro_deserializer 
}

consumer = DeserializingConsumer(consumer_config)
consumer.subscribe(['thermostat_readings'])

print("Listening for Avro data...")

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None or msg.error():
            continue
            
        # THE MAGIC: msg.value() is NO LONGER raw binary.
        # The Deserializer already did all the work. It is a perfect Python dictionary!
        payload = msg.value()
        
        print(f"🌡️ Sensor {payload['sensor_id']} reads {payload['temperature']}°C")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()