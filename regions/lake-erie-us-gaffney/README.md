# Workflow for Katie Gaffney's US Lake Erie basins

## Basin IDs and some information

Original shapefiles received from Katie Gaffney as Google Drive link
on August 28, 2023. Contains only shapefiles; no CSV file with basin list.

Remove commas and spaces in file names:
```
cd regions/lake-erie-us-gaffney/
\ls ~/Downloads/Shape\ files/*.zip > basins_original.csv
mkdir  ~/Downloads/Shape_files/
while read -r line; do echo $line ; new=$( echo "$line" | cut -d . -f 1 | tr ' ' '_' | tr -d ',') ; echo "${new}.zip" ; echo '' ; mv "${line}" "${new}.zip" ; done < basins_original.csv
zip ~/Downloads/20230828_Katie_Shape_files_raw.zip ~/Downloads/Shape_files/*.zip
```
Move resulting file to `regions/lake-erie-us-gaffney/`.

Starting CSV file with generic IDs:
```
files=$( \ls ~/Downloads/Shape_files/*.zip )
cc=0
echo "id,name,lat,lon,obs_q" > basins.csv
for ff in $files ; do basinname=$( echo $ff | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1 | tr '_' ' ') ; cc=$((cc+1)) ; echo "$(printf '%03d' ${cc}),${basinname},,," ; done >> basins.csv
```


## Standardize provided basin shapefiles

Extract data from Katie Gaffney's shapefiles. This means the correct
coordinate reference system (ESPG=4326) is added and only the largest
geometry is saved in a new shapefile.

```bash
# unzip raw file
cd basin-fabric/regions/lake-erie-us-gaffney/
unzip 20230828_Katie_Shape_files_raw.zip
cd 20230828_Katie_Shape_files_raw
files=$( \ls *.zip ) ; for ff in $files ; do unzip $ff -d $( echo $ff | cut -d '.' -f 1 ) ; done

# convert raw shapefiles
cd basin-fabric/src
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
./03_convert_shapefiles.sh -s lake-erie-us-gaffney

# remove unzipped folder
cd basin-fabric/regions/lake-erie-us-gaffney/
rm -r 20230828_Katie_Shape_files_raw
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s lake-erie-us-gaffney
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
python 05_retrieve_observations.py -s lake-erie-us-gaffney -p 1980-01-01:2018-12-31
```

Creates: observations/daily_streamflow.nc


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 06_static_attributes_geophysical.py -s lake-erie-us-gaffney
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
cd src
python 07_create_lumped_forcings.py -s lake-erie-us-gaffney -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc






## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s wisconsin-lewis -f 'rdrs-v2.1_north-america' -p 'all'
```

Creates: attributes/climate_indices_rdrs-v2.1_north-america.csv
Creates: forcings/*_agg_rdrs-v2.1_north-america_lp_daily_local.nc

Add produced files to Git:
```
git add regions/wisconsin-lewis/forcings/*/*_agg_*_daily_local.nc
```


## Merge observations and forcings

No LSTM will be trained here since there are no observations for these
basins available. But to evaluate other trained LSTMs of other regions
over this region, the forcings in neural-hydrology format will be
needed.

```
source env-3.10/bin/activate
python src/09_merge_forcings_and_observations.py -s 'wisconsin-lewis'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x wisconsin-lewis-v1
```


## Run validation experiment

Just run the basins of this region using another pre-trained
LSTM. This consists of several steps. It might be better to run them
one after each other by setting `do_XXX` to `True` one after each other.

```
source env-cuda/bin/activate
python 14_run_validation_experiments.py -s wisconsin-lewis -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
python 14_run_validation_experiments.py -s wisconsin-lewis -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
```

## Plot results of validation experiment

Plots results of validation experiment as time series per basin. All
validation experiments available will be plotted in the same plot (per
basin):

```
source env-3.10/bin/activate
python 15_plot_results_validation_experiments.py -s wisconsin-lewis -p 1980-01-01:2018-12-31
```
