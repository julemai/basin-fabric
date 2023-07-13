# Workflow for GRIP-GL basins

## Basins outlines

Basin outlines were created by Hongren Shen in GRIP-GL project. Mostly
based on North American routing product v2.1 but with a few extra
(manual) adjustments. Not reproducible.



## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```

```


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
python 04_plot_basin_map.py -s Wisconsin -g map_wisconsin
```


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
python src/05_static_attributes_geophysical.py -s Wisconsin
```


## Clip forcings

Extract forcings for each basin from RDRS-v2.1.

```
source env-3.10/bin/activate
python src/06_create_lumped_forcings.py -s Wisconsin
```


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
python src/07_static_attributes_forcings.py -s Wisconsin
```
