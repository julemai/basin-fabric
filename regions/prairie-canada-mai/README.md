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

Extract data from Hai's shapefile (shapefiles_prairie-canada-mai.zip
--> NC_bsns_25finalsubs.shp). This means the correct
coordinate reference system (ESPG=4326) is added and one shapefile
created per basin.

```bash
# unzip raw file
cd basin-fabric/regions/prairie-canada-mai/
unzip shapefiles_prairie-canada-mai_20240723.zip

# convert raw shapefiles
cd basin-fabric/src
pyenv activate env-3.11.9
./03_convert_shapefiles.sh -s prairie-canada-mai

# remove unzipped folder
cd basin-fabric/regions/prairie-canada-mai/
rm -r shapefiles_prairie-canada-mai_20240723
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.11.9
cd basin-fabric/src
python 04_plot_basin_map.py -s prairie-canada-mai
```

Creates: maps/map.png


## Retrieve observations

Retrieves streamflow observations for streamflow gauge stations listed
in column `obs_q` in `basins.csv`. Data are either retrieved from
downloaded HYDAT database
(`data/observations/streamflow/Hydat.sqlite3`) or directly from
USGS. Data should be downloaded at least for the period the forcings
will be available for (option -p).

```
pyenv activate env-3.11.9
python 05_retrieve_observations.py -s prairie-canada-mai -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


No observations found for the following stations:
'05DEU01', '05DFU01', '05ECU01', '05EDU01', '05EFU01'

Guessing that these are stations stations' data is to be extracted
from estimated Weekly Naturalized Flow which Dr. Amin collected from
another project in Alberta. Then we can treat as natural flows. These
stations are not available in ECCC data. They are all listed in
"NC_bsns_natualizedflows.shp" (i.e., '05AK001', '05CK004', '05DEU01',
'05DFU01', '05ECU01', '05EDU01', '05EFU01'). 


info of station 05AK001: {'name': 'SOUTH SASKATCHEWAN RIVER AT HIGHWAY
NO. 41', 'lat': 50.73749923706055, 'lon': -110.09583282470705,
'area_km2': 66000.0, 'Q': {'start': '1966-04-01', 'end':
'1993-12-31'}} 

info of station 05CK004: {'name': 'RED DEER RIVER NEAR BINDLOSS',
'lat': 50.90269088745117, 'lon': -110.29949951171876, 'area_km2':
47800.0, 'Q': {'start': '1960-10-01', 'end': '2022-12-31'}} 


TODO :: Need to get observations as provided by Hai


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
pyenv activate env-3.11.9
python 06_static_attributes_geophysical.py -s prairie-canada-mai
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
pyenv activate env-3.11.9
python src/07_create_lumped_forcings.py -s prairie-canada-mai -b XXXX -f /project/6070465/julemai/blended-model-na/data_in/rdrs_v2.1/annual/ -y graham
```

Creates: forcings/*_agg_annual_lp.nc

Need to be renamed:
```
files=$( \ls regions/prairie-canada-mai/forcings/*/*_agg_annual_lp.nc)
for ff in $files ; do ss=$( echo $ff ) ; ss2=$( echo "${ss/annual/rdrs-v2.1_north-america}" ) ; echo $ss ; echo $ss2 ; echo "" ; cp $ss $ss2 ; done
```

Creates: forcings/*_agg_rdrs-v2.1_north-america_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.11/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s prairie-canada-mai -f 'rdrs-v2.1_north-america' -p 'all' -a
```

Creates: attributes/climate_indices_rdrs-v2.1_north-america.csv
Creates: forcings/*_agg_rdrs-v2.1_north-america_lp_daily_local.nc

Add produced files to Git:
```
git add regions/prairie-canada-mai/forcings/*/*_agg_*_daily_local.nc
```






## Merge observations and forcings

No LSTM will be trained here since there are no observations for these
basins available. But to evaluate other trained LSTMs of other regions
over this region, the forcings in neural-hydrology format will be
needed.

```
source env-3.10/bin/activate
python src/09_merge_forcings_and_observations.py -s prairie-canada-mai  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x prairie-canada-mai-v1
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
