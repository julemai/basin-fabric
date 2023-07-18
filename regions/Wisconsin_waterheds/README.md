# Workflow for Wisconsin basins

## Basin IDs and some information

1. Original file provided by Nandita Basu (email) on June 1, 2023:
   WI priority lakes for watershed analysis.csv
2. Julie removed unnecessary columns:
   basins.csv

## Extract basins from routing product

Extract data from North American routing product v2.1
```
pyenv activate ravenpy
cd basin-fabric/src
./01_extract_shapefiles.sh -s Wisconsin
```

Creates: shapefiles/*/*_ds.*


## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```
pyenv activate ravenpy
cd basin-fabric/src
./02_create_lumped_shapefile.sh -s Wisconsin
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s Wisconsin
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 05_static_attributes_geophysical.py -s Wisconsin
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin from RDRS-v2.1.

```
source env-3.10/bin/activate
python 06_create_lumped_forcings.py -s Wisconsin
```


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
python 07_static_attributes_forcings.py -s Wisconsin
```
