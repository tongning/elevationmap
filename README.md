This repository contains a set of scripts for generating and visualizing street grade data. Uses python 3.

## How to use
1. First, download USGS elevation data IMG files. You can run `download_dc_usgs.sh` to download data for DC,
or you can download the files manually if you are looking for another region.

2. In `elevationfetchers.py`, update the `rasters` variable with the names of all of your IMG files from USGS.

3. Download OpenStreetMap street data from https://overpass-turbo.eu/. Navigate to the region of interest and paste
the following query:

```
[out:json];

(
  // get cycle route relatoins
  way["highway"]({{bbox}});
);

out body;
>;
out skel qt;
```
Do NOT run the query; instead click Export->Raw data directly from Overpass API. Save the resulting file
to the root of this repository as `streets.json`.

4. Use https://github.com/tyrasd/osmtogeojson to convert `streets.json` to `streets.geojson`.

5. Install python requirements using `pip install -r requirements.txt`. You may need to install the gdal development
package for your distribution first.

6. Run `elevationfetcher.py`. This should create a file named `slopes.json`.

7. Copy `slopes.json` to the `viz` folder. Serve the contents of `viz` as a static webpage to see the visualization.