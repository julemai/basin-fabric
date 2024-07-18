# LSTM experiment: north-america-mai

query-replace:
- XXXX with "region" to use,     e.g., 'north-america-mai'
- YYYY with "forcing" to use,    e.g., 'rdrs-v2.1_north-america'
- ZZZZ with "experiment" to use, e.g., 'north-america-mai-a-test'

## Get forcings and observations
```
source env-3.11/bin/activate
python 09_merge_forcings_and_observations.py -s 'north-america-mai'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x 'north-america-mai-v1'
```

Creates: lstm/north-america-mai-v1/basins/basins_with_obs.txt
Creates: lstm/north-america-mai-v1/basins/basins_without_obs.txt
Creates: lstm/north-america-mai-v1/time_series/<basins_with_obs>.nc


## Create LSTM setups
```
cd lstm/north-america-mai-v1/
cp ../_new_template/README.md .
mkdir runs
mkdir final-training
cp ../_new_template/final-training/seed*.yml final-training/.
```

## Adjust setups
Some settings might need to be adjusted; especially the name of the experiment <experiment> --> 'north-america-mai-v1':
```
cd lstm/north-america-mai-v1/final-training
files=$( \ls seed*.yml )
for ff in $files ; do sed "s/<experiment>/north-america-mai-v1/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

Or, for example, the end date of the calibration period:
```
for ff in $files ; do sed "s/\/2010/\/2018/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

## Link attributes
```
cd lstm/north-america-mai-v1/
mkdir attributes
cd attributes
ln -s ../../../regions/north-america-mai/attributes/static_attributes.csv .
ln -s ../../../regions/north-america-mai/attributes/climate_indices_rdrs-v2.1_north-america.csv climate_indices.csv
```


## Test settings

### Request interactive node with GPU
```
# cd /scratch/julemai/basin-fabric/
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=64G --ntasks=1 --account=def-julemai --gpus-per-node=1
```

### Load some modules
```
module load mpi4py/3.1.4
```

### Load Python environment
Load an environment that has NeuralHydrology and cuda etc.
```
source /home/julemai/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
```

### Do training
Each of these take about 3h20.
```
cd /home/julemai/projects/def-julemai/julemai/lstm/north-america-mai-v1/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml
```

### Submit job for training
Or submit a job (revise submit-script first):
```
cd /home/julemai/projects/def-julemai/julemai/lstm/north-america-mai-v1/
sbatch submit-cedar-train-lstm.sh
```


### Restart job for training
In case training was not finished, add this to submit script instead
of using `nh-run train --config-file
final-training/seed${SLURM_ARRAY_TASK_ID}.yml` where `AAAA` (e.g., 1206) and `BBBBBB`
(e.g., 075810) need to be adjusted to the IDs that the initial training used:
```
nh-run continue_training --run-dir runs/north-america-mai-v1-finalTraining-seed${SLURM_ARRAY_TASK_ID}_AAAA_BBBBBB/
```

Then just copy all `*.pt` files in `continue_training_from_epoch*` to
main folder (per seed), e.g.,
```
cd north-america-mai-v1-finalTraining-seed2_1206_075810/
cp continue_training_from_epoch*/*.pt .
```

### Run validation experiments
For example, evaluate all models on a new region (north-america-mai):
```
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=64G --ntasks=1 --account=def-julemai --gpus-per-node=1

module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f north-america-mai-v1
python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f north-america-mai-v1
python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f north-america-mai-v1
python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f north-america-mai-v1
python 14_run_validation_experiments.py -s north-america-mai -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1
```

For example, evaluate all regions with new model
(north-america-mai-v1) which can only be done when training of that
model is finished:
```
cd /home/julemai/projects/def-julemai/julemai/
salloc --time=04:00:00 --mem=64G --ntasks=1 --account=def-julemai --gpus-per-node=1 

module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 14_run_validation_experiments.py -s wisconsin-lewis      -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
python 14_run_validation_experiments.py -s ontario-zhi          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
python 14_run_validation_experiments.py -s grip-gl-mai          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3
python 14_run_validation_experiments.py -s conus-zhi            -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f conus-zhi-v1
python 14_run_validation_experiments.py -s camels-us-newman     -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
python 14_run_validation_experiments.py -s north-america-mai    -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1
```
