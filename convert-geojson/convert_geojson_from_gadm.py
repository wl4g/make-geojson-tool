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

import zipfile
from gevent import monkey
import gevent
import os
import sys
import signal

BATCH_TASKS = 3  # Add batch tasks count.
CONVERT_PRECISION = 0.01  # Convert to geojson from *.shp precision

os.environ['GEVENT_SUPPORT'] = 'True'
monkey.patch_all()  # Required for time-consuming operations

# current_dir = os.getcwd()
entrypoint_dir, entrypoint_file = os.path.split(
    os.path.abspath(sys.argv[0]))
output_dir = entrypoint_dir + "/output/"
os.makedirs(output_dir, exist_ok=True)


def do_convert(zip_work_dir, zip_name):
    for part in os.listdir(zip_work_dir):
        input_filename = zip_work_dir + '/' + part  # e.g: a/b/c.txt

        # if part.endswith(".dbf"):  # for extract country name
        #     os.system("mapshaper -i %s" % (input_filename))

        # Join paths, e.g: a/b/c.txt => c.json
        output_filename = output_dir + '/geojson/' + zip_name + '/' + \
            part[0:part.rindex('.')]+'.json'  # geojson

        if part.endswith(".shp"):  # for extract to genjson
            if not os.path.exists(output_filename):
                print("Converting for '%s'" % (part))

                os.system("mapshaper -i %s -proj latlon -o %s precision=%s" %
                          (input_filename, output_filename, CONVERT_PRECISION))
                # os.system("mapshaper -i %s -o %s" % (input_filename, output_filename))
            else:
                print("Skip has been converted for '%s'" % (part))


def convert_all():
    geodata_dir = entrypoint_dir + "/../fetch-geodata/output/"
    for f in os.listdir(geodata_dir):
        if f.endswith(".zip"):
            # e.g gadm40_RUS_shp.zip => gadm40_RUS_shp
            zip_name = f[0:f.rindex('.')]
            with zipfile.ZipFile(geodata_dir + f, 'r') as zip_ref:
                zip_work_dir = output_dir + zip_name
                os.makedirs(zip_work_dir, exist_ok=True)

                # Unzip the zip file.
                if len(os.listdir(zip_work_dir)) <= 0:
                    print("Extractall zip for '%s'" % (zip_name))
                    zip_ref.extractall(zip_work_dir)

                greenlets = []
                batchs = 0
                # for testing
                # print("add task for '%s'" % (zip_work_dir))
                # do_convert(zip_work_dir)

                greenlets.append(gevent.spawn(
                    do_convert, zip_work_dir, zip_name))
                if len(greenlets) % BATCH_TASKS == 0:
                    batchs += 1
                    print("[%d] Submit batch tasks ..." % (batchs))
                    gevent.joinall(greenlets, timeout=120)


if __name__ == "__main__":
    print('Starting GADM GeoJson Converter ...')
    try:
        os.nice(5)
        convert_all()
    except KeyboardInterrupt:
        print("Cancel convert tasks ...")
        # gevent.killall()
