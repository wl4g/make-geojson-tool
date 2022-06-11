# Make GeoJson Tools

## Codes Directories

```txt
.
├── converter
    ├── output ## Converted output assets directory. (Auto-Generate)
    ├── convert_geojson_from_gadm.py  ## Convert to geojson from GADM shapfile zip.
├── fetcher
    ├── output ## Fetched output assets directory. (Auto-Generate)
    ├── china
    │   ├── area_cn.csv  ## Fetch metadata of China geo data from Aliyun.
    │   ├── fetch_geodata_from_aliyun.py  ## Fetich global geographic data from Aliyun.
    │   └── legacy  ## Legacy outdated fetch scripts.
    │       ├── executor.sh  ## The concurrent executor tool implemented in pure shell.
    │       └── legacy_fetch_geodata_from_aliyun.sh  ## Pure shell implements of concurrently fetch China geodata from Alibyun (only China is supported)
    ├── output ## Fetched output assets directory. (Auto-Generate)
    ├── area_global.csv  ## Fetch metadata of global geo data from GADM.
    ├── fetch_geodata_from_gadm.py  ## Fetich global geographic data from GADM.
```

## Quick Start

- Preconditions

```bash
apt install -y nodejs
npm install -g mapshaper
mapshaper --help
```

- Building

```bash
git clone https://github.com/wl4g/make-geojson-tool
pip install -r requirements.txt
```

- Fetch `China` geo data from Aliyun (Only supports China)

```bash
./fetcher/china/fetch_geodata_from_aliyun.py

##    log:  ./log/fetcher_aliyun.log
## output: ./fetcher/china/output/
```

- Fetch `Any Countries` geo data from GADM (Supports Global), but the latest version may only support the [shapefile](https://gadm.org/formats.html) format, and you need to use tools such as [mapshaper](https://github.com/mbloch/mapshaper) to convert to [geojson](https://gadm.org/formats.html) format.

```bash
./fetcher/fetch_geodata_from_gadm.py

##    log:  ./log/fetcher.log
## output:  ./fetcher/output/
```

- Convert to [geojson](https://gadm.org/formats.html) format.

```bash
./converter/convert_geojson_from_gadm.py

##  input:  ./fetcher/output/
##    log:  ./log/converter.log
## output:  ./converter/output/geojson/
```
