# Workflow for Great Lakes basins


## Basin IDs and some information

1. File with basin IDs were provided by Wei Zhi May 22, 2023.
   Original file was: WQstations_100obs_TP_SRP.txt
2. Bibiana extracted basins where routing product exists:
   WQstations_100obs_TP_SRP_RP-exists.txt
3. Julie removed unnecessary columns:
   basins.csv


## Extract basins from routing product

Extract data from Ontario Routing Product v1.0
```
pyenv activate ravenpy
cd basin-fabric/src
./01_extract_shapefiles.sh -s Great-Lakes
```

Creates: shapefiles/*/*_ds.*


## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```
pyenv activate ravenpy
cd basin-fabric/src
./02_create_lumped_shapefile.sh -s Great-Lakes
```

Creates: shapefiles/*/*_lp.*

## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s Great-Lakes
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 05_static_attributes_geophysical.py -s Great-Lakes
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/06_create_lumped_forcings.py -s Great-Lakes -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_static_attributes_forcings.py -s Great-Lakes
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc
