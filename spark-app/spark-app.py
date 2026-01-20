import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, LongType

kafka_bootstrap = "kafka1:9092,kafka2:9093,kafka3:9094"
topic = "events_topic"
checkpoint_location = "/opt/spark/checkpoint"
jdbc_url = "jdbc:postgresql://postgres:5432/streamdb"
jdbc_props = {"user": "stream", "password": "stream", "driver": "org.postgresql.Driver"}

spark = (
    SparkSession.builder.appName("HAStreamingApp")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

schema = StructType(
    [
        StructField("id", LongType()),
        StructField("event_type", StringType()),
        StructField("timestamp", StringType()),
    ]
)

raw_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap)
    .option("subscribe", topic)
    .option("startingOffsets", "earliest")
    .load()
)

parsed = raw_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select(
    col("data.id").alias("id"),
    col("data.event_type").alias("event_type"),
    col("data.timestamp").cast("timestamp").alias("event_ts"),
)

agg = (
    parsed.withWatermark("event_ts", "10 minutes")
    .groupBy(
        window(col("event_ts"), "5 minutes"),
        col("event_type"),
    )
    .count()
)

def write_batch(df, batch_id):
    (df.withColumn("window_start", col("window.start"))
       .withColumn("window_end", col("window.end"))
       .drop("window")
       .write.mode("overwrite")
       .option("truncate", "false")
       .jdbc(jdbc_url, "event_aggregates", properties=jdbc_props)
    )

query = (
    agg.writeStream.outputMode("update")
    .foreachBatch(write_batch)
    .option("checkpointLocation", checkpoint_location)
    .start()
)

query.awaitTermination()