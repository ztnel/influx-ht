# -*- coding: utf-8 -*-
"""
Influx
======
Influx DB portal
"""

import logging


# bind logging to config file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s"
)
