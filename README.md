# Kafka-Spark Resilience Pipeline

Containerized streaming pipeline using Kafka and Spark Structured Streaming with chaos testing to verify zero data loss and fast recovery after broker and worker failures.

## Components

- Producer service: generates synthetic events and sends them to Kafka.
- Kafka + Zookeeper cluster: durable, replicated message backbone for events.
- Spark Structured Streaming app: consumes Kafka, aggregates with checkpoints for recovery.
- Sink (PostgreSQL or Parquet): stores aggregated results persistently.
- Chaos script: randomly kills Kafka brokers and Spark workers to test resilience.
- Validation script: checks that no events were lost after chaos testing.
- submission.yml: defines automated steps to build, run, test, and stop the pipeline.
