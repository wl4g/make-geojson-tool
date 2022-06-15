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
from bs4 import BeautifulSoup
from gevent import monkey
import gevent
import random
import re
import time
import os
import sys
import logging

BATCH_TASKS = 10  # Add batch tasks count.

os.environ['GEVENT_SUPPORT'] = 'True'

# current_dir = os.getcwd()
entrypoint_dir, entrypoint_file = os.path.split(
    os.path.abspath(sys.argv[0]))

output_dir = entrypoint_dir + "/output/"
os.makedirs(output_dir, exist_ok=True)

log_dir = entrypoint_dir + "/../log"
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir + '/fetch_zipcode_from_postinfo.log'

# see:https://docs.python.org/3/howto/logging.html#logging-to-a-file
logging.basicConfig(filename=log_file, filemode='w',
                    format='%(asctime)s [%(levelname)7s] %(threadName)s %(filename)s:%(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %l:%M:%S', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

monkey.patch_all()  # Required for time-consuming operations
# sys.settrace()


def do_fetch(url):
    logging.info('Fetching for %s' % (url))
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        if resp.status == 200:
            html = resp.read()
            return BeautifulSoup(html)
        else:
            raise RuntimeError(
                "Failed to fetch response status %s, url: %s" % resp.status, url)
    except Exception as e:
        logging.error("Failed to fetch for %s. reason: %s" % (url, e))


def do_parse(zipcode_page_url, country_short, country_long, region):
    output_file = output_file = get_output_file(country_short, country_long)
    bsObj = do_fetch(zipcode_page_url)
    try:
        container = bsObj.find("div", {"class": "container"})
        p = container.find("p")
        zipcode = p.find("a").find("strong").text
        line = country_short + "," + country_long + "," + region + "," + zipcode
        logging.info("Parsed: %s" % line)

        with open(output_file, "a", encoding="utf-8") as zipcodefile:
            zipcodefile.write(line)
            zipcodefile.write('\n')

    except AttributeError as ex:
        print("page has lost some attributes, but don't worry!", ex)
        with open(output_file + ".err", "w", encoding="utf-8") as geofile:
            errjson = {
                "url": zipcode_page_url,
                "country_long": country_long,
                "country_short": country_short,
                "region": region,
                "errmsg": ("ERROR: Failed to fetch for %s/%s:%s, caused by: %s" %
                           (country_short, country_long, zipcode_page_url, ex))
            }
            geofile.write(json.dumps(errjson))
            geofile.close


def get_output_file(country_short, country_long):
    return output_dir + country_short + ".csv"


def fetch_country_hierarchy(domain_uri, country_short, country_long):
    bsObj = do_fetch(domain_uri)
    output_file = get_output_file(country_short, country_long)
    if os.path.exists(output_file):
        logging.warning("Skip fetched of '%s'" % (output_file))
        return
    try:
        a_arr = bsObj.find("div", {"class": "cnt"}).find_all("a")
        for a in a_arr:
            region = a.text
            region = region[0:region.index('(')].strip()
            group_url = domain_uri + a.attrs['href']
            bsObj2 = do_fetch(group_url)
            div_cnt = bsObj2.find("div", {"class": "cnt"})
            # table = div_cnt.find_parent("table")
            tr_arr = div_cnt.find_all("tr")
            if len(tr_arr) > 0:  # page e.g:http://andorra.postcode.info/
                for tr in tr_arr:
                    td_arr = tr.find_all("td")
                    for td in td_arr:
                        # expect e.g:http://china.postcode.info/anhui/aiguo-township
                        zipcode_page_url = group_url + \
                            '/' + td.find("a").attrs['href']
                        do_parse(zipcode_page_url, country_short,
                                 country_long, region)
                        time.sleep(random.random()*10)

            else:  # page e.g:http://china.postcode.info/
                div_letterbutton = div_cnt.find(
                    "div", {"class": "letterbutton"})
                a_arr2 = div_letterbutton.find_all("a")
                for a2 in a_arr2:
                    group_url2 = group_url + '/' + a2.attrs['href']
                    bsObj3 = do_fetch(group_url2)
                    div_cnt2 = bsObj3.find("div", {"class": "cnt"})
                    # table = div_cnt.find_parent("table")
                    tr_arr = div_cnt2.find_all("tr")
                    for tr in tr_arr:
                        td_arr = tr.find_all("td")
                        for td in td_arr:
                            # expect e.g:http://china.postcode.info/anhui/aiguo-township
                            zipcode_page_url = group_url + \
                                '/' + td.find("a").attrs['href']
                            do_parse(zipcode_page_url, country_short,
                                     country_long, region)
                            time.sleep(random.random()*10)

    except AttributeError as ex:
        logging.error("Failed to fetch parse page for %s. reason: %s" %
                      (domain_uri, ex))


def fetch_all():
    err_files = [f for f in os.listdir(
        '.') if re.match(r'[a-zA-Z0-9]+.*\.err', f)]
    if len(err_files) <= 0:
        logging.info("Full new fetching ...")
        bsObj = do_fetch("http://postcode.info")
        try:
            greenlets = []
            batchs = 0

            table = bsObj.find("div", {"class": "cnt"}).find("table")
            # tbody = table.find("tbody")
            # tr_arr = tbody.find_all("tr")
            tr_arr = table.find_all("tr")
            for tr in tr_arr:
                td_arr = tr.find_all("td")
                for td in td_arr:
                    a_arr = td.find_all("a")
                    for a in a_arr:
                        country = a.text
                        country_short = country[0:country.index('=')].strip()
                        country_long = country[country.index('=')+1:]
                        country_long = country_long[0:country_long.index(
                            '(')].strip()
                        domain_url = a.attrs['href']

                        # for testing
                        # if country_short == "AD":
                        #     logging.info("%s/%s: %s", country_short,
                        #                  country_long, domain_url)
                        #     fetch_country_hierarchy(
                        #         domain_url, country_short, country_long)

                        greenlets.append(gevent.spawn(
                            fetch_country_hierarchy, domain_url, country_short, country_long))
                        if len(greenlets) % BATCH_TASKS == 0:
                            batchs += 1
                            logging.info(
                                "[%d] Submit batch tasks ..." % (batchs))
                            gevent.joinall(greenlets, timeout=300)

        except AttributeError as ex:
            print("page has lost some attributes, but don't worry!", ex)
    else:
        logging.info("Continue last uncompleted or failed fetch tasks from '%s'" %
                     (output_dir))
        greenlets = []
        batchs = 0
        for f in err_files:
            errjsonStr = ""
            errfileStr = output_dir + "/" + f
            with open(errfileStr, "r", encoding="utf-8") as errfile:
                while True:
                    line = errfile.readline(1024)
                    if len(line) <= 0:
                        break
                    errjsonStr += line

            errjson = json.loads(errjsonStr)
            url = errjson['url']
            country_short = errjson['country_short']
            country_long = errjson['country_long']
            region = errjson['region']
            # errmsg = errjson['errmsg']

            # Continue add batch fetch tasks.
            greenlets.append(gevent.spawn(
                do_parse, url, country_short, country_long, region))
            if len(greenlets) % BATCH_TASKS == 0:
                batchs += 1
                logging.info(
                    "[%d] Submit batch tasks ..." % (batchs))
                gevent.joinall(greenlets, timeout=300)
            # Remove older err json file.
            os.remove(errfileStr)


def statistics():
    success = 0
    failure = 0
    for f in os.listdir(output_dir):
        if f.endswith(".err"):
            failure += 1
        else:
            success += 1
    logging.info("-----------------------------------------------")
    logging.info("FETCHED Completed of SUCCESS: %d / FAILURE: %d" %
                 (success, failure))
    logging.info("-----------------------------------------------")


if __name__ == "__main__":
    # see:https://docs.python.org/zh-cn/3/library/functions.html#print
    print('Starting ZipCode Fetcher ...', flush=True)
    print(('Log See: %s' % (log_file)), flush=True)
    try:
        fetch_all()
        statistics()
    except KeyboardInterrupt:
        logging.warning("Cancel fetch tasks ...")
        gevent.killall(timeout=3)
