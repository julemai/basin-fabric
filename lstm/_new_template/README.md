# LSTM experiment: XXXX

query-replace:
- XXXX with "region" to use,     e.g., 'grip-gl-mai'
- YYYY with "forcing" to use,    e.g., 'rdrs-v2.1_north-america'
- ZZZZ with "experiment" to use, e.g., 'grip-gl-mai-a-test'

## Get forcings and observations
```
source env-3.10/bin/activate
python 09_merge_forcings_and_observations.py -s 'XXXX'  -f 'YYYY' -o 'daily_streamflow.nc' -p 'forcing' -x 'ZZZZ'
```

Creates: lstm/ZZZZ/basins/basins_with_obs.txt
Creates: lstm/ZZZZ/basins/basins_without_obs.txt
Creates: lstm/ZZZZ/time_series/<basins_with_obs>.nc


## Create LSTM setups
```
cd lstm/ZZZZ/
cp ../_new_template/README.md .
mkdir runs
mkdir final-training
cp ../_new_template/final-training/seed*.yml final-training/.
```

## Adjust setups
Some settings might need to be adjusted; especially the name of the experiment <experiment> --> 'ZZZZ':
```
cd lstm/ZZZZ/final-training
files=$( \ls seed*.yml )
for ff in $files ; do sed "s/<experiment>/ZZZZ/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

Or, for example, the end date of the calibration period:
```
for ff in $files ; do sed "s/\/2010/\/2018/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

## Link attributes
```
cd lstm/ZZZZ/
mkdir attributes
cd attributes
ln -s ../../../regions/XXXX/attributes/static_attributes.csv .
ln -s ../../../regions/XXXX/attributes/climate_indices_rdrs-v2.1_north-america.csv climate_indices.csv
```


## Test settings

### Request interactive node with GPU
```
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=4G --ntasks=1 --account=def-julemai --gpus-per-node=1
```

### Load some modules
```
module load mpi4py/3.1.4
```

### Load Python environment
Load an environment that has NeuralHydrology and cuda etc.
```
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
```

### Do training
Each of these take about 3h20.
```
cd /home/julemai/projects/def-julemai/julemai/lstm/ZZZZ/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml
```

### Submit job for training
Or submit a job (revise submit-script first):
```
cd /home/julemai/projects/def-julemai/julemai/lstm/ZZZZ/
sbatch submit-cedar-train-lstm.sh
```


### Restart job for training
In case training was not finished, add this to submit script instead
of using `nh-run train --config-file
final-training/seed${SLURM_ARRAY_TASK_ID}.yml` where `AAAA` (e.g., 1206) and `BBBBBB`
(e.g., 075810) need to be adjusted to the IDs that the initial training used:
```
nh-run continue_training --run-dir runs/ZZZZ-finalTraining-seed${SLURM_ARRAY_TASK_ID}_AAAA_BBBBBB/
```


Then just copy all `*.pt` files in `continue_training_from_epoch*` to
main folder (per seed), e.g.,
```
cd ZZZZ-finalTraining-seed2 _AAAA_BBBBBB/
cp continue_training_from_epoch*/*.pt .
```


### Run validation experiments
For example, evaluate all models on a new region (XXXX):
```
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=64G --ntasks=1 --account=def-julemai --gpus-per-node=1

module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 14_run_validation_experiments.py -s XXXX -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f ZZZZ
python 14_run_validation_experiments.py -s XXXX -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f ZZZZ
python 14_run_validation_experiments.py -s XXXX -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f ZZZZ
python 14_run_validation_experiments.py -s XXXX -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f ZZZZ
python 14_run_validation_experiments.py -s XXXX -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f ZZZZ
```

For example, evaluate all regions with new model
(ZZZZ) which can only be done when training of that
model is finished:
```
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=64G --ntasks=1 --account=def-julemai --gpus-per-node=1

module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 14_run_validation_experiments.py -s wisconsin-lewis      -u ZZZZ -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u ZZZZ -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
python 14_run_validation_experiments.py -s ontario-zhi          -u ZZZZ -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s grip-gl-mai          -u ZZZZ -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3
python 14_run_validation_experiments.py -s conus-zhi            -u ZZZZ -p 1980-01-01:2018-12-31 -f conus-zhi-v1
python 14_run_validation_experiments.py -s camels-us-newman     -u ZZZZ -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
python 14_run_validation_experiments.py -s XXXX                 -u ZZZZ -p 1980-01-01:2018-12-31 -f ZZZZ
```
