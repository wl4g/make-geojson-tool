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

import logging
import zipfile
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
log_file = log_dir + '/convert_geojson_from_shpfiles.log'

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


def do_convert(zip_work_dir, zip_name):
    for part in os.listdir(zip_work_dir):
        input_file = zip_work_dir + '/' + part  # e.g: a/b/c.txt

        # if part.endswith(".dbf"):  # for extract country name
        #     os.system("mapshaper -i %s" % (input_file))

        # e.g: gadm40_CHN_0.shx => gadm40_CHN_0
        geojson_file = part[0:part.rindex('.')]
        # e.g: gadm40_CHN_0 => CHN_0
        geojson_file = geojson_file[geojson_file.index('_')+1:]

        # e.g: '..../convert_geojson/geojson/output/json/CHN/CHN_0.json'
        output_file = output_dir + '/json/' + \
            geojson_file[0:geojson_file.rindex(
                '_')] + '/' + geojson_file+'.json'

        if part.endswith(".shp"):  # for extract to genjson
            if os.path.exists(output_file):
                logging.warning("Skip converted of '%s'" % (part))
            else:
                logging.info("Converting for '%s'" % (part))

                os.system("mapshaper -i %s -proj latlon -o %s precision=%s" %
                          (input_file, output_file, CONVERT_PRECISION))
                # os.system("mapshaper -i %s -o %s" % (input_file, output_file))


def convert_all():
    zip_shpfiles_dir = entrypoint_dir + "/../fetch_gadm/output/"
    for f in os.listdir(zip_shpfiles_dir):
        if f.endswith(".zip"):
            # e.g gadm40_RUS_shp.zip => gadm40_RUS_shp
            zip_name = f[0:f.rindex('.')]
            zip_filename = zip_shpfiles_dir + f
            try:
                with zipfile.ZipFile(zip_filename, 'r') as zip_file:
                    zip_work_dir = output_dir + "/.tmp-shpfiles/" + zip_name
                    os.makedirs(zip_work_dir, exist_ok=True)

                    # Unzip the zip file.
                    if len(os.listdir(zip_work_dir)) <= 0:
                        logging.info("Extractall zip for '%s'" % (zip_name))
                        zip_file.extractall(zip_work_dir)

                    greenlets = []
                    batchs = 0

                    # for testing
                    # logging.info("add task for '%s'" % (zip_work_dir))
                    # do_convert(zip_work_dir, zip_name)

                    greenlets.append(gevent.spawn(
                        do_convert, zip_work_dir, zip_name))
                    # all_greenlets.append(greenlets)

                    if len(greenlets) % BATCH_TASKS == 0:
                        batchs += 1
                        logging.info("[%d] Submit batch tasks ..." % (batchs))
                        gevent.joinall(greenlets, timeout=120)
            except Exception as e:
                logging.warning(
                    "Could't to extractall and processing of zip %s, caused by: %s" % (zip_filename, e))


if __name__ == "__main__":
    # see:https://docs.python.org/zh-cn/3/library/functions.html#print
    print('Starting GADM GeoJson Converter ...', flush=True)
    print(('Log See: %s' % (log_file)), flush=True)
    try:
        # signal.signal(signal.SIGINT, signal_handler)
        convert_all()
    except KeyboardInterrupt as e:
        logging.warning("Cancel convert tasks ...")
        gevent.killall(timeout=3)
