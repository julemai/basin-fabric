# Workflow for North American basins

## Extract basins from routing product

Extract data from Wei Zhi's shapefiles. This means the correct
coordinate reference system (ESPG=4326) is added and only the largest
geometry is saved in a new shapefile.
```

```


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
python 04_plot_basin_map.py -s North-America -g map_north-america
```


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
python src/05_static_attributes_geophysical.py -s North-America
```


## Clip forcings

Extract forcings for each basin from RDRS-v2.1.

```
source env-3.10/bin/activate
python src/06_create_lumped_forcings.py -s North-America
```


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
python src/07_static_attributes_forcings.py -s North-America
```
