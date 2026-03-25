from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# 1. Connect to the Schema Registry Server
sr_config = {
    'url': 'https://psrc-YOUR-ENDPOINT.confluent.cloud',
    'basic.auth.user.info': 'SR_API_KEY:SR_API_SECRET'
}
schema_registry_client = SchemaRegistryClient(sr_config)

# 2. The Contract (Usually loaded from a .avsc file using open('schema.avsc').read())
schema_str = """
{
  "namespace": "com.company.iot",
  "name": "ThermostatReading",
  "type": "record",
  "fields": [
    {"name": "sensor_id", "type": "int"},
    {"name": "temperature", "type": "float"}
  ]
}
"""

# 3. Create the Serializer (This handles the Magic Byte and Caching!)
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

# 4. Configure the Serializing Producer
producer_config = {
    'bootstrap.servers': 'pkc-YOUR-ENDPOINT.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'KAFKA_API_KEY',
    'sasl.password': 'KAFKA_API_SECRET',
    'acks': 'all',
    # --- THE BOUNCER ---
    'value.serializer': avro_serializer 
}

producer = SerializingProducer(producer_config)

# 5. Produce the Data
valid_data = {"sensor_id": 42, "temperature": 25.5}

print("Validating against schema and sending...")
producer.produce(topic='thermostat_readings', value=valid_data)
producer.flush()
print("✅ Data successfully serialized and sent!")