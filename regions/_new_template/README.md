# Template for new region

Fill all these folders with the according basin-specific data,
i.e. shapefiles of basins in this region.

Then use the following steps as template to document what was
done. Remove steps that are not necessary and add information that is
new (also add this to template for later use:





# Workflow for XXXX basins


## Extract basins from routing product

Extract data from XXXX's shapefiles. This means the correct
coordinate reference system (ESPG=4326) is added and only the largest
geometry is saved in a new shapefile.
```

```


## Extract basins from routing product

Extract data from XXXX Routing Product vXXXX
```

```

## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```

```

## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
python 04_plot_basin_map.py -s XXXX -g map_XXXX
```


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
python src/05_static_attributes_geophysical.py -s XXXX
```


## Clip forcings

Extract forcings for each basin from RDRS-v2.1.

```
source env-3.10/bin/activate
python src/06_create_lumped_forcings.py -s XXXX
```


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
python src/07_static_attributes_forcings.py -s XXXX
```
