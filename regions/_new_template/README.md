# Template for new region

Fill all these folders with the according basin-specific data,
i.e. shapefiles of basins in this region or list of basins
(basins.csv) and derive shapefiles with steps 01-03.

Then use the following steps as template to document what was
done. Remove steps that are not necessary and add information that is
new (also add this to template for later use:





# Workflow for XXXX basins



## Extract basins from routing product

Extract data from XXXX Routing Product vXXXX
```
pyenv activate ravenpy
cd basin-fabric/src
./01_extract_shapefiles.sh -s XXXX
```

Creates: shapefiles/*/*_ds.*


## Create lumped shapefiles

Routing product files are distributed setups. They need to be
converted into lumped geometries.
```
pyenv activate ravenpy
cd basin-fabric/src
./02_create_lumped_shapefile.sh -s XXXX
```

Creates: shapefiles/*/*_lp.*


## Standardize provided basin shapefiles

Extract data from XXXX's shapefiles. This means the correct
coordinate reference system (ESPG=4326) is added and only the largest
geometry is saved in a new shapefile.
```
pyenv activate env-3.8.5-ravenpy-new
cd basin-fabric/src
./03_convert_shapefiles.sh -s XXXX
```

Creates: shapefiles/*/*_lp.*


## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s XXXX
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-ravenpy-new
python src/05_static_attributes_geophysical.py -s XXXX
```

Creates: attributes/static_attributes.csv


## Clip forcings

Extract forcings for each basin XXXX from RDRS-v2.1.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/06_create_lumped_forcings.py -s XXXX -b XXXX -f XXXX -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source env-3.10/bin/activate
pyenv activate env-3.8.5-basin-fabric
python src/07_static_attributes_forcings.py -s XXXX
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc
