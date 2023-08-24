# LSTM experiment: CAMELS-US

This experiment is using the 671 CAMELS-US basins for training. The
forcings are RDRS-v2.1. The hyper-parameter settings are chosen based
on Gauch (2021, see Tab. D1):

Gauch, M., Kratzert, F., Klotz, D., Nearing, G. S., Lin, J., &
Hochreiter, S. (2021). Rainfall–runoff prediction at multiple
timescales with a single Long Short-Term Memory network. Hydrology and
Earth System Sciences, 25,
2045–2062. http://doi.org/10.5194/hess-25-2045-2021

batch = 256
hidden = 256
learn = {0:0.001, 10:0.0005,25=0.0001}
epochs = 30
dropout = 0.4
seq_length = 365



## Get forcings and observations
```
source env-3.10/bin/activate
python 09_merge_forcings_and_observations.py -s 'camels-us-newman'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x camels-us-newman-v1
```

Creates: lstm/<experiment>/basins/basins_with_obs.txt<br>
Creates: lstm/<experiment>/basins/basins_without_obs.txt<br>
Creates: lstm/<experiment>/time_series/<basins_with_obs>.nc<br>


## Create LSTM setups
```
cd lstm/<experiment>/
mkdir runs
mkdir final-training
cp ../<experiment>/final-training/seed*.yml final-training/.
```

## Adjust setups
Some settings might need to be adjusted; especially the name of the experiment "camels-us-newman".
```
cd lstm/camels-us-newman-v1/final-training
files=$( \ls seed*.yml )
for ff in $files ; do sed "s/<experiment>/camels-us-newman-v1/g" ${ff} > tmp.tmp ; mv tmp.tmp ${ff} ; done
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
ln -s ../../../regions/camels-us-newman/attributes/static_attributes.csv .
ln -s ../../../regions/camels-us-newman/attributes/climate_indices_rdrs-v2.1_north-america.csv climate_indices.csv
```

## Test settings

### Request interactive node with GPU
```
cd /scratch/julemai/basin-fabric/
salloc --time=04:00:00 --mem=4G --ntasks=1 --account=def-julemai --gpus-per-node=1 --cpus-per-task=4
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
cd /scratch/julemai/basin-fabric/lstm/camels-us-newman-v1/
nh-run train --config-file final-training/seed1.yml
nh-run train --config-file final-training/seed2.yml
...
nh-run train --config-file final-training/seed10.yml
```

### Submit job for training
Or submit a job (revise submit-script first):
```
cd /scratch/julemai/basin-fabric/lstm/camels-us-newman-v1/
sbatch submit-cedar-train-lstm.sh
```
