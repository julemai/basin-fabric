# Workflow for Andrew Newman's CAMELS US basins

## Basin IDs and some information

Download data from:
https://ral.ucar.edu/solutions/products/camels

Create `basins.csv`:
```bash
# get ID and name
cat camels_name.txt | cut -d ';' -f 1,3 | tr -s ';' '@' | tr -s ','
';' | tr -s '@' ',' > tmp.csv

# get lat, lon and obs_q
while read p ; do bb=$( echo "${p}" | cut -d ',' -f 1 ) ; topo=$( grep ^"${bb};" camels_topo.txt ) ; lat=$( echo $topo | cut -d ";" -f 2 ) ; lon=$( echo $topo | cut -d ";" -f 3 ) ; echo "${p},${lat},${lon},${bb}" ; done < tmp.csv > basins.csv
```

## Standardize provided basin shapefiles

Extract data from CAMELS shapefile. This means the correct
coordinate reference system (ESPG=4326) is added and one shapefile
created per basin.

```bash
# unzip raw file
cd basin-fabric/regions/camels-us-newman/
unzip HCDN_nhru_final_671.zip

# convert raw shapefiles
cd basin-fabric/src
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
./03_convert_shapefiles.sh -s camels-us-newman

# remove unzipped folder
cd basin-fabric/regions/camels-us-newman/
rm -r HCDN_nhru_final_671
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
source env-3.10/bin/activate
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s camels-us-newman
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
python 05_retrieve_observations.py -s camels-us-newman -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc



## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 06_static_attributes_geophysical.py -s conus-zhi
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s conus-zhi -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s conus-zhi -f 'rdrs-v2.1_north-america' -p 'all'
```

Creates: attributes/climate_indices_rdrs-v2.1_north-america.csv
Creates: forcings/*_agg_rdrs-v2.1_north-america_lp_daily_local.nc

Add produced files to Git:
```
git add regions/conus-zhi/forcings/*/*_agg_*_daily_local.nc
```
