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
import logging
from gevent import monkey
import gevent
import os
import sys
import signal

BATCH_TASKS = 3  # Add batch tasks count.
CONVERT_PRECISION = 0.01  # Convert to geojson from *.shp precision

os.environ['GEVENT_SUPPORT'] = 'True'

# current_dir = os.getcwd()
entrypoint_dir, entrypoint_file = os.path.split(
    os.path.abspath(sys.argv[0]))

output_dir = entrypoint_dir + "/output"
os.makedirs(output_dir, exist_ok=True)

log_dir = entrypoint_dir + "/../log"
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir + '/convert_zipcode_from_genjson.log'

# see:https://docs.python.org/3/howto/logging.html#logging-to-a-file
logging.basicConfig(filename=log_file, filemode='w',
                    format='%(asctime)s [%(levelname)7s] %(threadName)s %(filename)s:%(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %l:%M:%S', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

monkey.patch_all()  # Required for time-consuming operations
# all_greenlets = []


# signal handler to process after catch ctrl+c command
# def signal_handler(signum, frame):
#     logging.info("Signal handler ...")
#     gevent.joinall(all_greenlets)
#     gevent.killall(all_greenlets, block=True, timeout=3)
#     gevent.kill(block=True)
#     sys.exit(0)


# Postcodes data from: http://postcode.info/
def do_transform_geojson(geojson_input_file):
    geojson_filename = os.path.basename(geojson_input_file)
    geo_name = geojson_filename[0:geojson_filename.rindex('_')]
    mapping_csv = entrypoint_dir + '/input/' + geo_name + '.csv'

    mapping_list = ""
    with open(mapping_csv, "r", encoding="utf-8") as mapfile:
        while True:
            line = mapfile.readline(1024)
            if len(line) <= 0:
                break
            mapping_list += line

    geojson_str = ""
    with open(geojson_input_file, "r", encoding="utf-8") as geojsonfile:
        while True:
            line = geojsonfile.readline(1024)
            if len(line) <= 0:
                break
            geojson_str += line

    geojson = json.loads(geojson_str)
    for feature in geojson['features']:
        properties = feature['properties']
        # TODO
        print("TODO")
        print("TODO")
        print("TODO")
        print(properties)


def do_convert(geojson_dir, geojson_dirname):
    for geojson_filename in os.listdir(geojson_dir):
        geojson_input_file = geojson_dir + '/' + geojson_filename

        geojson_output_dir = output_dir + '/' + geojson_dirname
        os.makedirs(geojson_output_dir, exist_ok=True)

        # e.g: '..../converter/zipcode/output/CHN/CHN_0.json'
        geojson_output_file = geojson_output_dir + '/' + geojson_filename

        if os.path.exists(geojson_output_file):
            logging.warning("Skip converted of '%s'" % (geojson_filename))
        else:
            logging.info("Converting for '%s'" % (geojson_filename))
            with open(geojson_output_file + ".json", "w", encoding="utf-8") as geojsonfile:
                geojsonfile.write(do_transform_geojson(geojson_input_file))


def convert_all():
    geojson_root_dir = entrypoint_dir + "/../geojson/output/json"
    for geojson_dirname in os.listdir(geojson_root_dir):
        try:
            # e.g: '..../converter/geojson/output/json/CHN'
            geojson_dir = geojson_root_dir + '/' + geojson_dirname

            greenlets = []
            batchs = 0

            # for testing
            # logging.info("add task for '%s'" % (geojson_dir))
            # do_convert(geojson_dir, geojson_dirname)

            greenlets.append(gevent.spawn(
                do_convert, geojson_dir, geojson_dirname))
            # all_greenlets.append(greenlets)

            if len(greenlets) % BATCH_TASKS == 0:
                batchs += 1
                logging.info("[%d] Submit batch tasks ..." % (batchs))
                gevent.joinall(greenlets, timeout=120)
        except Exception as e:
            logging.warning(
                "Could't to processing of geojson %s, caused by: %s" % (geojson_dir, e))


if __name__ == "__main__":
    # see:https://docs.python.org/zh-cn/3/library/functions.html#print
    print('Starting GeoJson With ZipCode Converter ...', flush=True)
    print(('Log See: %s' % (log_file)), flush=True)
    try:
        # signal.signal(signal.SIGINT, signal_handler)
        convert_all()
    except KeyboardInterrupt as e:
        logging.warning("Cancel convert tasks ...")
        gevent.killall(timeout=3)
