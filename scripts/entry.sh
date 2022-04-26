#!/bin/bash
HOST="$(cut -d'/' -f3<<<"$INFLUXDB_ADDR" | cut -d':' -f1)"
PORT="$(cut -d'/' -f3<<<"$INFLUXDB_ADDR" | cut -d':' -f2)"

# wait for influx container
./scripts/wfi.sh -h "$HOST" -p "$PORT" -t 30

python3 -m tests 