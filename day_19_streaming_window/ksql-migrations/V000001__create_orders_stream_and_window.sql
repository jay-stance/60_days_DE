-- Step 1: Register the Stream
-- Because you used Schema Registry, ksqlDB already knows your columns!
CREATE STREAM orders_stream WITH (
  KAFKA_TOPIC='orders',
  VALUE_FORMAT='AVRO'
);

-- Step 2: The Tumbling Window Table
-- This query never stops running. It continuously updates the aggregations.
CREATE TABLE hourly_item_sales AS
  SELECT 
    itemid,
    SUM(orderunits) AS total_units_sold,
    COUNT(*) AS total_orders
  FROM orders_stream
  WINDOW TUMBLING (SIZE 1 HOUR)
  GROUP BY itemid
  EMIT CHANGES;