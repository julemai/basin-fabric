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
cd /scratch/julemai/basin-fabric/
salloc --time=04:00:00 --mem=4G --ntasks=1 --account=def-julemai --gpus-per-node=1
```

### Load some modules
```
module load mpi4py/3.1.3
```

### Load Python environment
Load an environment that has NeuralHydrology and cuda etc.
```
source /scratch/julemai/basin-fabric/env-cuda/bin/activate
```

### Do training
Each of these take about 3h20.
```
cd /scratch/julemai/basin-fabric/lstm/north-america-mai-v1/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml
```

### Submit job for training
Or submit a job (revise submit-script first):
```
cd /scratch/julemai/basin-fabric/lstm/north-america-mai-v1/
sbatch submit-cedar-train-lstm.sh
```
