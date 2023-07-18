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
pip install dask --no-index
pip install rasterio --no-index
pip install timezonefinder --no-index
pip install ipython --no-index
pip install -U pytest --no-index

pip install statsmodels --no-index  # for ravenpy
pip install haversine               # for ravenpy
pip install --no-index pydantic     # for ravenpy
pip install --no-index pymbolic     # for ravenpy
pip install --no-index cf_xarray    # for ravenpy

pip install ravenpy[gis] --no-dependencies
pip install neuralhydrology
```

### On MacOS

```
pyenv virtualenv 3.8.5 env-3.8.5-basin-fabric
pyenv activate env-3.8.5-basin-fabric

pip install --upgrade pip

pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
pip install argparse
pip install numpy
pip install scipy
pip install geopandas
pip install geojson
pip install rasterio
pip install fiona
pip install netCDF4
pip install xarray
pip install dask
pip install matplotlib
pip install timezonefinder
python -m pip install basemap
pip install -U pytest

pip install ravenpy[gis]
pip install neuralhydrology
pip install hydroDL  # didnt work

# optional
pip install ipython
pip install jupyter
```

### Run CUDA on Graham

```
# Login to Cedar
ssh -Y julemai@cedar.computecanada.ca

# Request interactive node with GPU
cd /scratch/julemai/basin-fabric/
salloc --time=03:20:00 --mem=3G --ntasks=1 --account=def-julemai --gpus-per-node=1

# Load some modules
module load mpi4py/3.1.3

# Load Python env
source /scratch/julemai/basin-fabric/env-cuda/bin/activate

# Do training
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml

# Do some stuff
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-run evaluate --run-dir test

### DOES NOT FIND
scaler_file = run_dir / "train_data" / "train_data_scaler.yml"
```
