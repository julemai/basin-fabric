# Workflow for DUCs 8 wetland basins


## Basin IDs and some information

Original GeoJSON shapefile received from Luana Camelo as Slack message
on April 21, 2025. Contains shapes. Luana also provided CSV with basin
list. The lat/lon represents the wetlands' centroid assuming here to be the "pour point"; in WGS1984.

Create shapefile for the 8 GoJSON features by adding this to end of `coords2shapefile.py`:
```
path_to_file = '../../regions/duc8-camelo/4326_HydrologyAnalyst_Basins.geojson'

import geojson
import geopandas as gpd
import json

with open(path_to_file) as f:
   gj = geojson.load(f)

nfeatures = len(gj['features'])
for ifeature in range(nfeatures):

   basin = gj['features'][ifeature]['properties']['id']
   filename = '../../regions/duc8-camelo/shapefiles/{}/{}_lp'.format(basin,basin)

   print('Working on basin {}'.format(basin))

   # write shapefile
   coords = gj['features'][ifeature]['geometry']['coordinates'][0]
   coords2shapefile(filename,coords)

   # write as GeoJSON
   shape_subbasins = gpd.read_file(filename+'.shp')  # is a GeoPandas DataFrame
   json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
   with open(filename+".json", "w") as outfile:
       json.dump(json_dict, outfile)
```



## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s duc8-camelo
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

The wetlands are so tiny that some require `all_touched=True` for the
SOIL data.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python src/06_static_attributes_geophysical.py -s duc8-camelo
```

Creates: attributes/static_attributes.csv


## Clip nutrients

Extract nutrients for each basin duc8-camelo from gTREND-P-Canada_v1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric

basins='BL DY FE KE LL MA MO OH'
for bb in $basins ; do python 07_create_lumped_forcings_gTREND-P-CA_v1.py -s duc8-camelo -b ${bb} -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_35 -y mac ; done
```

Creates: forcings/*_agg_*_*_lp.nc

