# Workflow for wq-us-chang basins


## Standardize provided basin shapefiles

Extract data from GeoPackage shared by Shuyu Chang April
22, 2025 (WQP_US_WSHD_5070_Finalized_09172024.gpkg). This means the correct
coordinate reference system from ESPG:5070 to ESPG=4326. Saving only
largest geometry in new shapefile per basin.
```
pyenv activate env-3.8.5-ravenpy-new
cd basin-fabric/src
./03_convert_shapefiles.sh -s wq-us-chang
```

```
python ../regions/wq-us-chang/shapefiles/read_gpkg.py
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s wq-us-chang
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
python 05_retrieve_observations.py -s wq-us-chang -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python src/06_static_attributes_geophysical.py -s wq-us-chang
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin wq-us-chang from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s wq-us-chang -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc



## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s wq-us-chang -f 'rdrs-v2.1_north-america' -p 'all'
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc

```
Add produced files to Git:
```
git add regions/wq-us-chang/forcings/*/*_agg_*_daily_local.nc
```
