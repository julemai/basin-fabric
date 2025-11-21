# Workflow for wq-ca-mai basins


## Obtain basin shapefiles

We are using the Datastream (C) stations delineated Sep 22, 2025. In total
there is 10,234 basins (in geojson format). 

We need to select (C) basins smaller than 10,000 km2 as most LSTM models
will have issue with larger ones. We also want to select basins that
have data between 1980-01-01 and 2018-12-31 which is the period we
have RDRS-v2.1 forcings for. Then we want to add the information of
co-located (Q) stations.

The basins have to fullfil the following criteria:
* Have C observations of any solute (soluble P, TP, nitrate, or TN)
  between 1980 and 2018
* C basin can not be entirely located above 60N (no DEM)
* Basin needs to be smaller than 10,000 km2
* We will later potentially also have to exclude the basins smaller
  than 300 km2 but for now we keep them.

All this can be done by running:
```
python ../regions/wq-ca-mai/shapefiles/get_data.py
```

Creates: shapefiles/*/*_lp.json
Creates: basins_w_small_basins.csv   --> used: copied to basins.csv
Creates: basins_wo_small_basins.csv


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s wq-ca-mai
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
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-ravenpy-new
python 05_retrieve_observations.py -s wq-ca-mai -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-ravenpy-new
python src/06_static_attributes_geophysical.py -s wq-ca-mai
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin wq-ca-mai from RDRS-v2.1.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s wq-ca-mai -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc







## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s wq-ca-mai -f 'rdrs-v2.1_north-america' -p 'all' -a
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc

Add produced files to Git:
```
git add regions/wq-ca-mai/forcings/*/*_agg_*_daily_local.nc
```


## Check and plot attribute values

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/17_plot_attributes.py -s 'wq-ca-mai' -f 'rdrs-v2.1_north-america'
```

Creates: Wrote: /project/6070465/julemai/basin-fabric/src/../regions/wq-ca-mai/attributes/climate_indices_rdrs-v2.1_north-america.pdf


## Check forcings

Checks the forcing files and ranges of variables:
```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/18_check_all_forcing_files.py -s 'wq-ca-mai' -f 'rdrs-v2.1_north-america' 
```
