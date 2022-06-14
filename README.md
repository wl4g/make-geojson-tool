# Make GeoJson Tools

## 1. Codes Directories

```txt
.
├── convert_geojson
        ├── output ## Converted output assets directory. (Auto-Generate)
        ├── convert_geojson_from_shpfiles.py  ## Convert to geojson from GADM shapfile zip.
    convert_zipcode
        ├── input ## Fetching input mapping configuration. (Manual)
        |       ├── area_global.csv  ## Fetch metadata of global geo data from GADM.
        ├── output ## Converted output assets directory. (Auto-Generate)
        ├── convert_zipcode_from_geojson.py  ## Convert from raw geojson to geojson with zipcode.
    fetch_aliyun
        ├── china
            ├── input ## Fetching input mapping configuration. (Manual)
            |   ├── area_cn.csv  ## Fetch metadata of China geo data from Aliyun.
            ├── output ## Fetched output assets directory. (Auto-Generate)
            ├── fetch_geojson_from_aliyun.py  ## Fetich global geographic data from Aliyun.
            └── legacy  ## Legacy outdated fetch scripts.
                ├── executor.sh  ## The concurrent executor tool implemented in pure shell.
                └── legacy_fetch_geojson_from_aliyun.sh  ## Pure shell implements of concurrently fetch China geodata from Alibyun (only China is supported)
    fetch_gadm
        ├── input ## Fetching input mapping configuration. (Manual)
        |   ├── area_global.csv  ## Fetch metadata of global geo data from GADM.
        ├── output ## Fetched output assets directory. (Auto-Generate)
        ├── fetch_shpfiles_from_gadm.py  ## Fetich global geographic data from GADM.
    fetch_zipcode
        ├── input ## Fetching input mapping configuration. (Manual)
        |   ├── area_global.csv  ## Fetch metadata of global geo data from GADM.
        ├── output ## Fetched output assets directory. (Auto-Generate)
        ├── fetch_zipcode_from_postinfo.py  ## (bs4/BeautifulSoup based crawlers)Fetich global zipcode from postcode.info.
```

## 2. Quick Start

### 2.1 Building

```bash
git clone https://github.com/wl4g/make-geojson-tool
pip install -r requirements.txt
```

### 2.2 Fetch `China` geo data from Aliyun (Only supports China)

```bash
./fetcher/china/fetch_geojson_from_aliyun.py

##  input: ./fetch_aliyun/china/input/area_cn.csv
## output: ./fetch_aliyun/china/output/
##    log: ./log/fetch_geojson_from_aliyun.log
```

### 2.3 Fetch `Any Countries` geo data from GADM (Supports Global), but the latest version may only support the [shapefile](https://gadm.org/formats.html) format, and you need to use tools such as [mapshaper](https://github.com/mbloch/mapshaper) to convert to [geojson](https://gadm.org/formats.html) format

```bash
./fetch_gadm/fetch_shpfiles_from_gadm.py

##  input: https://geodata.ucdavis.edu/gadm/gadm4.0/shp/
## output: ./fetch_gadm/output/
##    log: ./log/fetch_shpfiles_from_gadm.log
```

### 2.4 Convert to [geojson](https://gadm.org/formats.html) format from GADM shpfiles

- Preconditions

```bash
apt install -y nodejs
npm install -g mapshaper
mapshaper --help
```

```bash
./convert_geojson/convert_geojson_from_shpfiles.py

##  input:  ./fetch_geojson/output/
## output:  ./convert_geojson/output/geojson/
##    log:  ./log/convert_geojson_from_shpfiles.log
```

### 2.5 Fetch zipcodes/postcodes from [https://postcode.info](https://postcode.info)

```bash
./convert_zipcode/fetch_zipcode_from_postinfo.py

##  input:  https://postcode.info/
## output:  ./fetch_zipcode/output/
##    log:  ./log/fetch_zipcode_from_postinfo.log
```

### 2.6 Convert to geojson with zipcodes/postcodes

```bash
./convert_zipcode/convert_zipcode_from_genjson.py

##  input:  ./fetch_zipcode/output/
## output:  ./convert_zipcode/output/
##    log:  ./log/convert_zipcode_from_genjson.log
```
