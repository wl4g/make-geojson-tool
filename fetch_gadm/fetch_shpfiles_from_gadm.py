#!/bin/python3
# Copyright 2017 ~ 2025 the original author or authors. <wanglsir@gmail.com, 983708408@qq.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import urllib.request
from gevent import monkey
import gevent
from re import S
import csv
import os
import sys
import signal
import logging


# see:https://gadm.org/download_country_v3.html
# see:https://gadm.org/download_country.html
# e.g:https://geodata.ucdavis.edu/gadm/gadm4.0/shp/gadm40_USA_shp.zip
# e.g:https://geodata.ucdavis.edu/gadm/gadm4.0/shp/gadm40_CHN_shp.zip
# e.g:https://geodata.ucdavis.edu/gadm/gadm4.0/shp/gadm40_JPN_shp.zip
# e.g:https://geodata.ucdavis.edu/gadm/gadm4.0/shp/gadm40_GBR_shp.zip
GEO_BASE_URI = "https://geodata.ucdavis.edu/gadm/gadm4.0/shp/"
BATCH_TASKS = 10  # Add batch tasks count.

os.environ['GEVENT_SUPPORT'] = 'True'

# current_dir = os.getcwd()
entrypoint_dir, entrypoint_file = os.path.split(
    os.path.abspath(sys.argv[0]))

output_dir = entrypoint_dir + "/output/"
os.makedirs(output_dir, exist_ok=True)

log_dir = entrypoint_dir + "/../log"
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir + '/fetch_shpfiles_from_gadm.log'

# see:https://docs.python.org/3/howto/logging.html#logging-to-a-file
logging.basicConfig(filename=log_file, filemode='w',
                    format='%(asctime)s [%(levelname)7s] %(threadName)s %(filename)s:%(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %l:%M:%S', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

monkey.patch_all()  # Required for time-consuming operations


def do_fetch(gadmCountrySelectOptionValue, gadmCountrySelectOptionName):
    # see:view-source:https://gadm.org/download_country.html#L311
    suffix = "gadm40_" + \
        gadmCountrySelectOptionValue.split('_')[0] + "_shp.zip"
    url = GEO_BASE_URI + suffix
    saveFilename = output_dir + suffix
    logging.info('Fetching for %s - %s' % (gadmCountrySelectOptionName, url))
    try:
        urllib.request.urlretrieve(url, saveFilename)
    except Exception as e:
        logging.error("Failed to fetch for %s. reason: %s" % (suffix, e))
        with open(saveFilename + ".err", "w", encoding="utf-8") as geofile:
            errjson = {
                "url": url,
                "errmsg": ("ERROR: Failed to fetch for %s, caused by: %s" % (url, e))
            }
            geofile.write(json.dumps(errjson))
            geofile.close


def fetch_all():
    with open(entrypoint_dir + "/input/area_global.csv", "r", encoding="utf-8") as csvfile:
        greenlets = []
        batchs = 0
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            gadmCountrySelectOptionValue = row[0]
            gadmCountrySelectOptionName = row[1]
            logging.debug("add task for '%s/%s'" %
                          (gadmCountrySelectOptionValue, gadmCountrySelectOptionName))

            # for testing
            # do_fetch(gadmCountrySelectOptionValue, gadmCountrySelectOptionName)

            greenlets.append(gevent.spawn(
                do_fetch, gadmCountrySelectOptionValue, gadmCountrySelectOptionName))
            if len(greenlets) % BATCH_TASKS == 0:
                batchs += 1
                logging.info("[%d] Submit batch tasks ..." % (batchs))
                gevent.joinall(greenlets, timeout=300)


def statistics():
    success = 0
    failure = 0
    for f in os.listdir(output_dir):
        if f.endswith(".err"):
            failure += 1
        else:
            success += 1
    logging.info("-----------------------------------------------")
    logging.info("FETCHED Completed of SUCCESS: %d / FAILURE: %d" % (success, failure))
    logging.info("-----------------------------------------------")


if __name__ == "__main__":
    # see:https://docs.python.org/zh-cn/3/library/functions.html#print
    print('Starting GADM GeoData Fetcher ...', flush=True)
    print(('Log See: %s' % (log_file)), flush=True)
    try:
        fetch_all()
        statistics()
    except KeyboardInterrupt:
        logging.warning("Cancel fetch tasks ...")
        gevent.killall(timeout=3)
