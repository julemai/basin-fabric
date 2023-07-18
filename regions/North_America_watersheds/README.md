# Workflow for North American basins

## Basin IDs and some information

1. Original file provided by Wei Zhi:
   TP_site_basin513.txt
2. Julie removed unnecessary columns:
   basins.csv

## Standardize provided basin shapefiles

Extract data from Wei Zhi's shapefiles. This means the correct
coordinate reference system (ESPG=4326) is added and only the largest
geometry is saved in a new shapefile.

```bash
# unzip raw file
cd basin-fabric/regions/North_America_watersheds/
unzip 20230612_Wei_selected_US_sites_shapefile.zip

# convert raw shapefiles
cd basin-fabric/src
pyenv activate env-3.8.5-ravenpy-new
./03_convert_shapefiles.sh -s North-America

# remove unzipped folder
cd basin-fabric/regions/North_America_watersheds/
rm -r 20230612_Wei_selected_US_sites_shapefile
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s North-America
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 05_static_attributes_geophysical.py -s North-America
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/06_create_lumped_forcings.py -s North-America -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_static_attributes_forcings.py -s North-America
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc
