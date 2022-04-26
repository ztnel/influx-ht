
import os
import logging
import time
import threading
import queue
import random
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import WriteType
from influxdb_client.domain.write_precision import WritePrecision

_log = logging.getLogger(__name__)
q = queue.Queue()


def producer():
    measurement = "test"
    c = 0
    v = 0
    while True:
        time.sleep(5.4e-6)
        vnoise = random.uniform(-1, 1)
        cnoise = random.uniform(-1, 1)
        c += cnoise
        v += vnoise
        write_str = f"{measurement} c={c},v={v}"
        # _log.info("Generated lp: %s", write_str)
        q.put(write_str)


class TransferInfo:
    LATENCY = 1_000
    BATCH_SIZE = 5_000
    SAMPLE_RATE = 185_000


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
    batch_size=5000,            # optimal batch size for influx 2.x
    flush_interval=1000,        # flush the buffer every second if buffer is not filled
    jitter_interval=0,          # no jitter for simplicity
    retry_interval=3000
)


def sec_to_ns(ts) -> int:
    return int(ts * 1e9)


def sec_to_us(ts) -> int:
    return int(ts * 1e6)


buffer = []
sample_spacing = 1 / TransferInfo.SAMPLE_RATE
batch_sample_time = sample_spacing * TransferInfo.BATCH_SIZE
_log.info("Fixed Batch Sample Time: %ss", batch_sample_time)
_log.info("Sample Spacing: %ss", sample_spacing)
while True:
    timestamp = time.time_ns()
    _log.info("Now : %s", timestamp)
    batch_ts_start = timestamp - sec_to_ns(batch_sample_time)
    _log.info("Batch Start Computed Timestamp: %ss", batch_ts_start / 1e9)
    # get item from queue line by line and append a uniform timestamp equal to a predefined sample rate
    for i in range(TransferInfo.BATCH_SIZE):
        ws = q.get(block=True)
        wlp = f"{ws} {int((batch_ts_start + sec_to_ns(i * sample_spacing))/1000)}"
        buffer.append(wlp)
    _log.info("Obtained samples: %s", len(buffer))
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
