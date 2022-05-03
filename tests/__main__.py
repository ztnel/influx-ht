
import os
import logging
import time
import threading
import queue
import random
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import WriteType
from influxdb_client.domain.write_precision import WritePrecision


class TransferInfo:
    LATENCY = 1_000
    BATCH_SIZE = 1
    SAMPLE_RATE = 1  # samples per second
    SAMPLE_SPACING = 1 / SAMPLE_RATE


def producer():
    measurement = "test"
    c = 0
    v = 0
    while True:
        time.sleep(TransferInfo.SAMPLE_SPACING)
        vnoise = random.uniform(-1, 1)
        cnoise = random.uniform(-1, 1)
        c += cnoise
        v += vnoise
        write_str = f"{measurement} c={c},v={v}"
        # _log.info("Generated lp: %s", write_str)
        q.put(write_str)


def micros() -> int:
    return time.time_ns() // 1000


_log = logging.getLogger(__name__)
q = queue.Queue()
index = 0
buffer = []
stream_start_ts = micros()

# Read environment
influxdb_addr = os.environ['INFLUXDB_ADDR']
influxdb_token = os.environ['INFLUXDB_TOKEN']
influxdb_org = os.environ['INFLUXDB_ORG']
influxdb_bucket = os.environ['INFLUXDB_BUCKET']

_log.info("Influx Client")
_log.info("=============")
_log.info("InfluxDB Address: %s", influxdb_addr)
_log.info("InfluxDB Token: %s", influxdb_token)
_log.info("InfluxDB Org: %s", influxdb_org)
_log.info("InfluxDB Bucket: %s", influxdb_bucket)

client = InfluxDBClient(
    url=influxdb_addr,
    token=influxdb_token,
    org=influxdb_token
)

# Turn-on the worker thread.
_log.info("Starting producer thread")
threading.Thread(target=producer, daemon=True).start()

# Write options uses batching mode by default NOTE: all time units in ms
wo = WriteOptions(
    write_type=WriteType.asynchronous,
    batch_size=TransferInfo.BATCH_SIZE,       # optimal batch size for influx 2.x
    flush_interval=1000,                      # flush the buffer every second if buffer is not filled
    jitter_interval=0,                        # no jitter for simplicity
    retry_interval=3000
)

_log.info("Stream start timestamp: %s", stream_start_ts)
while True:
    # get item from queue line by line and append a uniform timestamp equal to a predefined sample rate
    for _ in range(TransferInfo.BATCH_SIZE):
        ws = q.get(block=True)
        wlp = f"{ws} {int(stream_start_ts + (index * TransferInfo.SAMPLE_SPACING)*1e6)}"
        index += 1
        buffer.append(wlp)
    wstart = time.perf_counter_ns()
    with client.write_api(write_options=wo) as wc:
        wc.write(
            influxdb_bucket,
            influxdb_org,
            buffer,
            write_precision=WritePrecision.US  # type:ignore
        )
    wend = time.perf_counter_ns()
    _log.info("Write execution speed: %s", (wend - wstart) / 1e9)
    buffer.clear()
