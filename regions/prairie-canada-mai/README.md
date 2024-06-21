# Workflow for Duc-Hai Nguyen's Canadian prairie basins


## Basin IDs and some information

1. File with basin IDs were provided by Duc-Hai Nguyen on June 12,
   2024 in a Google folder:
   - downstream_stns.csv (68)
   - headwater_stns.csv (67)
   - mountain_stns.csv (43)
   - ordinary_stns.csv (37)
   - prairies_stns.csv (55)


## Standardize provided basin shapefiles

Extract data from CAMELS shapefile. This means the correct
coordinate reference system (ESPG=4326) is added and one shapefile
created per basin.

```bash
# unzip raw file
cd basin-fabric/regions/prairie-canada-mai/
unzip shapefiles_prairie-canada-mai.zip

# convert raw shapefiles
cd basin-fabric/src
pyenv activate env-3.11.9
./03_convert_shapefiles.sh -s prairie-canada-mai

# remove unzipped folder
cd basin-fabric/regions/prairie-canada-mai/
rm -r shapefiles_prairie-canada-mai
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s prairie-canada-mai
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
python 05_retrieve_observations.py -s ontario-zhi -p 1980-01-01:2018-12-31
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
python src/08_static_attributes_forcings.py -s ontario-zhi -f 'rdrs-v2.1_north-america' -p 'all' -a
```

Creates: attributes/climate_indices_rdrs-v2.1_north-america.csv
Creates: forcings/*_agg_rdrs-v2.1_north-america_lp_daily_local.nc

Add produced files to Git:
```
git add regions/ontario-zhi/forcings/*/*_agg_*_daily_local.nc
```


## Merge observations and forcings

No LSTM will be trained here since there are no observations for these
basins available. But to evaluate other trained LSTMs of other regions
over this region, the forcings in neural-hydrology format will be
needed.

```
source env-3.10/bin/activate
python src/09_merge_forcings_and_observations.py -s 'ontario-zhi'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x ontario-zhi-v1
```


## Run validation experiment

Just run the basins of this region using another pre-trained
LSTM. This consists of several steps. It might be better to run them
one after each other by setting `do_XXX` to `True` one after each other.

```
source env-cuda/bin/activate
python 14_run_validation_experiments.py -s ontario-zhi -u conus-zhi-v1    	  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s ontario-zhi -u conus-zhi-v2    	  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s ontario-zhi -u grip-gl-mai-v2  	  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s ontario-zhi -u grip-gl-mai-v3  	  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s ontario-zhi -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
```

## Plot results of validation experiment

Plots results of validation experiment as time series per basin. All
validation experiments available will be plotted in the same plot (per
basin):

```
source env-3.10/bin/activate
python 15_plot_results_validation_experiments.py -s ontario-zhi -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31
```
