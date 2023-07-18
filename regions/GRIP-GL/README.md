# Workflow for GRIP-GL basins

## Basins outlines

Basin outlines were created by Hongren Shen in GRIP-GL project. Mostly
based on North American routing product v2.1 but with a few extra
(manual) adjustments. Not reproducible.



## Standardize provided basin shapefiles

Extract data from GRIP-GL's shapefiles. This just rename files into "*_lp.*".

```
# unzip raw file
cd basin-fabric/regions/GRIP-GL/
unzip shapefiles_raw.zip

# convert raw shapefiles
pyenv activate ravenpy
cd basin-fabric/src
pyenv activate env-3.8.5-ravenpy-new
./03_convert_shapefiles.sh -s GRIP-GL

# remove unzipped folder
cd basin-fabric/regions/GRIP-GL/
rm -r shapefiles_raw
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s GRIP-GL
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python 05_static_attributes_geophysical.py -s GRIP-GL
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin from RDRS-v2.1.

```
source env-3.10/bin/activate
python 06_create_lumped_forcings.py -s GRIP-GL
```


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
python 07_static_attributes_forcings.py -s GRIP-GL
```
