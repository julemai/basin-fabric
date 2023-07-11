# Welcome to the Basin Fabric

The Basin Fabric comprises codes to derive basin attributes, forcings,
etc to setup hydrologic and data-driven models. Codes are free to use
with proper attribution of the author.

<p align="center">
   <img alt="Basin Fabric logo. Created with tome.app" src="https://github.com/julemai/basin-fabric/blob/main/images/logo_basin-fabric.png" width="65%" />
</p>



## Setup Python Environment

### On Graham

```
module purge
module load StdEnv/2020 netcdf/4.7.4 gcc/9.3.0 gdal/3.5.1
module load mpi4py/3.1.3 proj/9.0.1
module load geos/3.10.2
module load nco/5.0.6
module load python/3.10.2

mkdir env-3.10
virtualenv --no-download env-3.10
source env-3.10/bin/activate

pip install --no-index --upgrade pip

pip install netCDF4 --no-index # no need, it is for raven-hydro
pip install GDAL --no-index
pip install numpy --no-index
pip install argparse --no-index
pip install geopandas --no-index
pip install geojson --no-index
pip install fiona --no-index
pip install scipy --no-index
pip install xarray --no-index
pip install rasterio --no-index
pip install ipython --no-index
pip install -U pytest --no-index

pip install statsmodels --no-index  # for ravenpy
pip install haversine               # for ravenpy
pip install --no-index pydantic     # for ravenpy
pip install --no-index pymbolic     # for ravenpy
pip install --no-index cf_xarray    # for ravenpy

pip install ravenpy[gis] --no-dependencies
```
