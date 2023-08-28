# Workflow for Julie Mai's GRIP-GL basins

## Basins outlines

Basin outlines were created by Hongren Shen in GRIP-GL project. Mostly
based on North American routing product v2.1 but with a few extra
(manual) adjustments. Not reproducible.



## Standardize provided basin shapefiles

Extract data from GRIP-GL's shapefiles. This just rename files into "*_lp.*".

```
# unzip raw file
cd basin-fabric/regions/grip-gl-mai/
unzip shapefiles_raw.zip

# convert raw shapefiles
pyenv activate ravenpy
cd basin-fabric/src
pyenv activate env-3.8.5-ravenpy-new
./03_convert_shapefiles.sh -s grip-gl-mai

# remove unzipped folder
cd basin-fabric/regions/grip-gl-mai/
rm -r shapefiles_raw
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s grip-gl-mai
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
python 05_retrieve_observations.py -s grip-gl-mai -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 06_static_attributes_geophysical.py -s grip-gl-mai
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin from RDRS-v2. This was done in GRIP-GL
and data have been just transferred from there (using Martin Gauch's
forcing.ipynb and forcings.py).

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s grip-gl-mai -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on RDRS-v2 meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s grip-gl-mai -f 'rdrs-v2_north-america' -p 'all'
```

Creates: attributes/climate_indices_rdrs-v2_north-america.csv
Creates: forcings/*_agg_rdrs-v2_north-america_lp_daily_local.nc


Derive attributes based on RDRS-v2.1 meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s grip-gl-mai -f 'rdrs-v2.1_north-america' -p 'all'
```

Creates: attributes/climate_indices_rdrs-v2.1_north-america.csv
Creates: forcings/*_agg_rdrs-v2.1_north-america_lp_daily_local.nc

Add produced files to Git:
```
git add regions/grip-gl-mai/forcings/*/*_agg_*_daily_local.nc
```
