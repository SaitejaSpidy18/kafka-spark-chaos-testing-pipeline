#!/usr/bin/env bash
set -e

SERVICES=("kafka1" "kafka2" "kafka3" "spark-worker-1" "spark-worker-2")

echo "Starting chaos test..."
END_TIME=$((SECONDS + 1800)) # 30 minutes

while [ $SECONDS -lt $END_TIME ]; do
  victim=${SERVICES[$RANDOM % ${#SERVICES[@]}]}
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - Stopping container: $victim"
  docker compose stop "$victim" || true

  sleep $((RANDOM % 60 + 30))

  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - Starting container: $victim"
  docker compose start "$victim" || true

  sleep $((RANDOM % 60 + 30))
done

echo "Chaos test finished."