High-Availability Streaming Pipeline with Chaos Testing :

This repository contains a fault-tolerant, end-to-end streaming data pipeline built with Kafka, Spark Structured Streaming, and PostgreSQL, with automated chaos testing and data validation to prove zero data loss under failures.

The project is designed to simulate a production-grade, mission-critical streaming system that can recover from node failures, broker restarts, and transient network issues while preserving data integrity.

1. System Architecture
The system consists of the following major components:

Data Producer

Generates a continuous stream of synthetic events (e.g., transactions, sensor readings) and publishes them to Kafka.


Kafka Cluster + Zookeeper

Multi-broker Kafka cluster (e.g., 3 brokers) managed via Docker.

Topics configured with replication and min.insync.replicas to tolerate broker failures.

Spark Structured Streaming Application

Consumes events from Kafka in near real-time.

Performs transformations, parsing, and optional aggregations.

Uses checkpointing and exactly-once/idempotent writes to the sink.

PostgreSQL Sink

Stores the processed events (and/or aggregates) in durable relational tables.

Acts as the source of truth for validation.

Chaos Testing Script (chaos.sh / chaos.py)

Randomly kills containers (Kafka brokers, Spark, producer, etc.), restarts them, and introduces controlled failures to test resilience.

Data Validation Script

Compares expected vs. actual event counts and identifiers between producer logs and PostgreSQL.

Proves that no messages were lost and that duplicates are either controlled or handled idempotently.

1.1 High-Level Architecture Diagram
text
         +------------------+
         |  Data Producer   |
         | (Python/Java)    |
         +---------+--------+
                   |
                   | 1. Events (JSON)
                   v
         +---------+--------+
         |   Kafka Topic    |
         | (Replicated N)   |
         +----+-----+-------+
              |     |
        2a    |     | 2b Replication
              v     v
        +-----+-----+------+
        | Kafka Brokers    |
        | (Broker 1..N)    |
        +----------+-------+
                   |
                   | 3. Stream read
                   v
         +---------+--------+
         | Spark Streaming  |
         |  (Checkpointed)  |
         +---------+--------+
                   |
                   | 4. Writes (Upserts)
                   v
         +---------+--------+
         |  PostgreSQL DB   |
         +---------+--------+
                   |
                   | 5. Validation Queries
                   v
         +---------+--------+
         | Validation Script|
         +------------------+
1.2 Chaos Testing Diagram
text
                     +-----------------------------+
                     |       Chaos Script         |
                     +--------------+-------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
          v                         v                         v
 +--------+--------+        +-------+--------+        +-------+--------+
 |  Kafka Broker 1 |        |  Spark Driver |        |  Producer App  |
 +--------+--------+        +-------+--------+        +-------+--------+
          ^                         ^                         ^
          |                         |                         |
          +-------------------------+-------------------------+
                                    |
                             +------+------+
                             |  Monitoring |
                             +-------------+
The chaos script periodically selects random targets (brokers, Spark, producer, etc.), stops and restarts them, while the pipeline continues to ingest and process events.

2. Prerequisites
Ensure the following are installed on your machine:

Docker (>= 20.x) and Docker Compose (>= 2.x)

Git

Python 3.x (if your producer/validation/chaos scripts are Python-based)

Java/Scala toolchain (if used by the producer or Spark app)

3. Repository Structure
Adapt this section to your actual repo layout:

text
.
├── docker-compose.yml
├── submission.yml
├── README.md
├── RESILIENCE_REPORT.md
├── producer/
│   ├── src/...
│   └── Dockerfile
├── spark-app/
│   ├── src/...
│   └── Dockerfile
├── chaos/
│   ├── chaos.sh
│   └── chaos.py
├── validation/
│   └── validate_data.py
└── db/
    ├── init.sql
    └── Dockerfile
Key files:

docker-compose.yml: Orchestrates Kafka, Zookeeper, Spark, PostgreSQL, and the producer.

submission.yml: Contains all commands for automated evaluation (setup, run, chaos, validation).

RESILIENCE_REPORT.md: Analysis of failures, recovery times, and data integrity proof.

chaos.sh / chaos.py: Chaos injection scripts.

validate_data.py (or similar): Data validation logic.

4. Setup Instructions
4.1 Clone the Repository
bash
git clone https://github.com/SaitejaSpidy18/kafka-spark-chaos-testing-pipeline.git
cd <kafka-spark-chaos-testing-pipeline>
4.2 Environment Configuration
Copy the sample environment file if provided:

bash
cp .env.example .env
Set the following typical variables (if used):

KAFKA_BROKERS=kafka-1:9092,kafka-2:9092,kafka-3:9092

KAFKA_TOPIC=events_topic

POSTGRES_HOST=postgres

POSTGRES_DB=streaming_db

POSTGRES_USER=stream_user

POSTGRES_PASSWORD=stream_password

Make sure the values match the service names and ports defined in docker-compose.yml.

4.3 Build and Start Services
Build all images:

bash
docker compose build
Start the full stack in the background:

bash
docker compose up -d
Verify containers:

bash
docker compose ps
You should see containers for Kafka brokers, Zookeeper, Spark (driver/worker), PostgreSQL, and the producer.

5. Running the Streaming Pipeline
5.1 Start the Kafka Cluster and PostgreSQL
If not already up:

bash
docker compose up -d zookeeper kafka-1 kafka-2 kafka-3 postgres
5.2 Initialize Database Schema
Run the initialization SQL (if not auto-run):

bash
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/init.sql
Adjust the path if your init.sql is mounted differently.

5.3 Start the Data Producer
If the producer runs as a separate service:

bash
docker compose up -d producer
Alternatively, run it manually (example):

bash
docker compose exec producer python /app/producer.py
The producer will:

Generate events at a configurable rate.

Publish them to the configured Kafka topic.

5.4 Start the Spark Streaming Application
If Spark is defined as a service:

bash
docker compose up -d spark
Or, using spark-submit inside the container (example):

bash
docker compose exec spark spark-submit \
  --class com.example.StreamingApp \
  --master local[*] \
  /app/spark-app.jar
Ensure that:

Kafka source is configured with the correct brokers and topic.

Checkpoint directory is set to a durable volume (e.g., /tmp/checkpoints on a Docker volume).

Sink writes to the PostgreSQL database with idempotent logic (e.g., upserts based on primary key).

6. Chaos Test: How to Run
The chaos test deliberately injects failures into the running system to verify its resilience.

6.1 Chaos Test Configuration
In chaos/chaos.sh or chaos/chaos.py, you will typically find parameters such as:

Target containers list (e.g., kafka-1, kafka-2, spark, producer)

Chaos duration (e.g., 300–900 seconds)

Interval between attacks (e.g., 30 seconds)

Failure actions (stop, restart, kill, network delay, etc.)

Adjust these parameters as needed for your environment.

6.2 Start the Chaos Test
From the repo root:

bash
# Example shell version
bash chaos/chaos.sh --duration 600 --interval 30

# Or, Python version
python chaos/chaos.py --duration 600 --interval 30
What the script does (conceptually):

Loops for the specified duration.

Randomly picks a service (e.g., kafka-2) and performs an action:

docker compose stop kafka-2

Wait a few seconds

docker compose start kafka-2

Logs each failure and recovery event.

While this runs, the producer and Spark job continue streaming, and Spark uses checkpointing plus Kafka offsets to recover without data loss.

7. Data Validation: Proving Zero Data Loss
The validation script compares the data produced vs. data stored in PostgreSQL to prove end-to-end integrity.

7.1 Expected vs Actual Data
Typical strategy:

Expected: Count and IDs of messages produced, derived from:

Producer logs

A metadata table in PostgreSQL that stores sequence ranges

Or a deterministic sequence (e.g., IDs 1..N)

Actual: Count and IDs of records in the sink table(s) in PostgreSQL.

7.2 Running the Validation Script
After the chaos test is complete and the system has stabilized (producer and Spark still running or gracefully stopped):

bash
python validation/validate_data.py \
  --producer-log-path logs/producer.log \
  --db-host localhost \
  --db-port 5432 \
  --db-name $POSTGRES_DB \
  --db-user $POSTGRES_USER \
  --db-password $POSTGRES_PASSWORD
Or, run inside the validation container:

bash
docker compose run --rm validation
The script should:

Connect to PostgreSQL.

Compute the expected number of events and their IDs.

Query the sink table(s) and compute the actual number of events and IDs.

Assert that:

No IDs are missing (no data loss).

Optional: duplicates are either absent or handled.

On success, it prints a pass message (e.g., VALIDATION PASSED: zero data loss). This is the primary success criterion.

8. Automated Run via submission.yml
The submission.yml file defines how the entire pipeline, chaos test, and validation are orchestrated automatically for evaluation.

A typical structure (conceptual):

text
setup:
  - docker compose build
  - docker compose up -d

start_pipeline:
  - docker compose up -d producer spark

run_chaos:
  - bash chaos/chaos.sh --duration 600 --interval 30

validate:
  - python validation/validate_data.py --config config/validation.yml
The evaluator will execute these sections in order to:

Build and start the environment.

Run the streaming pipeline.

Inject failures for a sustained duration.

Run the validation and check for zero data loss.

Ensure all commands in submission.yml are non-interactive and succeed without manual input.

9. Monitoring and Troubleshooting
Helpful commands:

View logs for a specific service:

bash
docker compose logs -f kafka-1
docker compose logs -f spark
docker compose logs -f producer
docker compose logs -f postgres
Check container health:

docker compose ps
Enter a container shell:

docker compose exec spark bash
docker compose exec postgres bash
Inspect PostgreSQL data:

docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
10. Cleanup
To stop and remove all containers, networks, and volumes created by this project:

docker compose down -v
This cleans up all resources, including Kafka logs, checkpoints, and database data, so use carefully.