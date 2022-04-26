import os
import logging
import time
from random import random
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client import Point

_log = logging.getLogger(__name__)

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
_log.info("%s instantiated successfully", __name__)
measurement = "test"

while True:
    c = round(random(), 2)
    v = round(random(), 2)
    point = Point("test").field("v", v).field("c", c)
    _log.info(str(point))
    # write_str = f"{measurement} c={c},v={v} {int(time.time()*1000)}"
    # _log.info("Line: %s", write_str)
    wstart = time.perf_counter_ns()
    with client.write_api(write_options=ASYNCHRONOUS) as wc:
        wc.write(
            influxdb_bucket,
            influxdb_org,
            point
        )
    wend = time.perf_counter_ns()
    _log.info("Write execution speed: %s", (wend - wstart) / 1e9)
    time.sleep(0.1)
