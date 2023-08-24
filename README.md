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
pip install pathlib2

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
salloc --time=04:00:00 --mem=4G --ntasks=1 --account=def-julemai --gpus-per-node=1 --cpus-per-task=4

# Load some modules
module load mpi4py/3.1.3

# Load Python env
source /scratch/julemai/basin-fabric/env-cuda/bin/activate

# Do training (each about 3h20)
# - first numbers: [number of basins]
# - second numbers (epoch): [number of timesteps * number of basins / batch_size]
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml

# Evaluate trained model (each about 2m30)
# - creates: runs/grip-gl-mai-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_metrics.csv
# - creates: runs/grip-gl-mai-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_results.p
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed1_XXXX_XXXXXX/
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed2_XXXX_XXXXXX/
...
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed10_XXXX_XXXXXX/

# Merge ensembles (average their predictions; take about 1min total)
# - creates: /scratch/julemai/basin-fabric/lstm/grip-gl-mai/final-training/test_ensemble_metrics.csv
# - creates: /scratch/julemai/basin-fabric/lstm/grip-gl-mai/final-training/test_ensemble_results.p
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-results-ensemble --run-dirs runs/grip-gl-finalTraining-seed* --output-dir final-training

# Get median KGE
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
ipy
import pandas as pd
data = pd.read_csv('final-training/test_ensemble_metrics.csv')
data['KGE_1D'].median()

# save settings and results
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
files=$( \ls runs/grip-gl-finalTraining-seed*/config.yml )
for ff in $files ; do cp $ff $ff.cal ; done
files=$( \ls runs/grip-gl-finalTraining-seed*/test/model_epoch030/test_results.p )
for ff in $files ; do cp $ff $ff.cal ; done
files=$( \ls runs/grip-gl-finalTraining-seed*/test/model_epoch030/test_metrics.csv )
for ff in $files ; do cp $ff $ff.cal ; done
cp /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_results.p /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_results.p.cal
cp /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_metrics.csv /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_metrics.csv.cal
```

# Validation
Save calibration configs
```
# Temporal validation: change start-date and end-date
files=$( \ls runs/grip-gl-finalTraining-seed*/config.yml )
for ff in $files ; do sed 's/test_end_date:\ 31\/12\/2018/test_end_date:\ 31\/12\/1999/g' ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
for ff in $files ; do sed 's/test_start_date:\ 01\/01\/2000/test_start_date:\ 01\/01\/1980/g' ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done

# Evaluate trained model (each about 2m30)
# - creates: runs/grip-gl-mai-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_metrics.csv
# - creates: runs/grip-gl-mai-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_results.p
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed1_XXXX_XXXXXX/
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed2_XXXX_XXXXXX/
...
nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed10_XXXX_XXXXXX/

# Merge ensembles (average their predictions; take about 1min total)
# - creates: /scratch/julemai/basin-fabric/lstm/grip-gl-mai/final-training/test_ensemble_metrics.csv
# - creates: /scratch/julemai/basin-fabric/lstm/grip-gl-mai/final-training/test_ensemble_results.p
cd /scratch/julemai/basin-fabric/lstm/grip-gl/
nh-results-ensemble --run-dirs runs/grip-gl-finalTraining-seed* --output-dir final-training

# save results
files=$( \ls runs/grip-gl-finalTraining-seed*/config.yml )
for ff in $files ; do cp $ff $ff.valtemp ; done
files=$( \ls runs/grip-gl-finalTraining-seed*/test/model_epoch030/test_results.p )
for ff in $files ; do cp $ff $ff.valtemp ; done
files=$( \ls runs/grip-gl-finalTraining-seed*/test/model_epoch030/test_metrics.csv )
for ff in $files ; do cp $ff $ff.valtemp ; done
cp /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_results.p /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_results.p.valtemp
cp /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_metrics.csv /scratch/julemai/basin-fabric/lstm/grip-gl/final-training/test_ensemble_metrics.csv.valtemp
```
