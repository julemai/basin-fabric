# Workflow for Julie Mai's North America basins


## Basins selected

5797 ... HYSETS basins larger than 300 km2
3646 ... 5 yrs data between 2001-2015
3152 ... North American Routing product v2.1 exists
2577 ... Basins smaller than 10,000 km2


## Extract basins from routing product

Extract data from North American Routing product v2.1
```
pyenv activate ravenpy
cd basin-fabric/src
./01_extract_shapefiles.sh -s north-america-mai
```

Creates: shapefiles/*/*_ds.*


## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```
pyenv activate ravenpy
cd basin-fabric/src
./02_create_lumped_shapefile.sh -s north-america-mai
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s north-america-mai
```

Creates: maps/map.png


## Retrieve observations

Retrieves streamflow observations for streamflow gauge stations listed
in clumn `obs_q` in `basins.csv`. Data are either retrieved from
downloaded HYDAT database
(`data/observations/streamflow/Hydat.sqlite3`) or directly from
USGS. Data should be downloaded at least for the period the forcings
will be available for (option -p).

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 05_retrieve_observations.py -s north-america-mai -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 06_static_attributes_geophysical.py -s ontario-zhi
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s ontario-zhi -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s ontario-zhi -f 'rdrs-v2_north-america' -p 'all'
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc

Add produced files to Git:
```
git add regions/ontario-zhi/forcings/*/*_agg_*_daily_local.nc
```
