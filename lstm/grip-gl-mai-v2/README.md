# LSTM experiment: GRIP-GL

This experiment is using the 212 (rather than 141) GRIP-GL basins for training. The
forcings are RDRS-v2.1 (rather than RDRS-v2 as used in GRIP-GL).

## Get forcings and observations
```
source env-3.10/bin/activate
python 09_merge_forcings_and_observations.py -s 'grip-gl-mai'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x grip-gl-mai
```

Creates: lstm/<experiment>/basins/basins_with_obs.txt<br>
Creates: lstm/<experiment>/basins/basins_without_obs.txt<br>
Creates: lstm/<experiment>/time_series/<basins_with_obs>.nc<br>


## Create LSTM setups
```
cd lstm/<experiment>/
mkdir runs
mkdir final-training
cp ../_new_template/final-training/seed*.yml final-training/.
```

## Adjust setups
Some settings might need to be adjusted; especially the name of the experiment "grip-gl-mai".
```
cd lstm/grip-gl-mai/final-training
files=$( \ls seed*.yml )
for ff in $files ; do sed "s/<experiment>/grip-gl-mai/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

Or end date of calibration period:
```
for ff in $files ; do sed "s/\/2010/\/2018/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
```

## Link attributes
```
cd lstm/<experiment>/
mkdir attributes
cd attributes
ln -s ../../../regions/grip-gl-mai/attributes/static_attributes.csv .
ln -s ../../../regions/grip-gl-mai/attributes/climate_indices_rdrs-v2.1_north-america.csv climate_indices.csv
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
Each of these take about 9h20.
```
cd /scratch/julemai/basin-fabric/lstm/grip-gl-mai/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml
```

### Submit job for training
Or submit a job (revise submit-script first):
```
cd /scratch/julemai/basin-fabric/lstm/grip-gl-mai/
sbatch submit-cedar-train-lstm.sh
```
