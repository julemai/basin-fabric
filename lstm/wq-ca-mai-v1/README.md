# LSTM experiment: wq-ca-mai-v1 (only predictions)

This experiment is using the 2650 WQ basins located in Canada (1998
have no Q station matched, 652 have Q station matched). These
are the basins that have observations of at least one solute during
1980-2018. The experiment provides the forcings in NeuralHydrology
format such that trained LSTMs can be used to create predictions of
streamflow for these basins. This dataset is NOT used to train an LSTM
because no or not enough observations of streamflow are available. 

## Get forcings and observations
```
source env-3.10/bin/activate
python 09_merge_forcings_and_observations.py -s 'wq-ca-mai'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x wq-ca-mai-v1
```

Creates: lstm/<experiment>/basins/basins_with_obs.txt<br>
Creates: lstm/<experiment>/basins/basins_without_obs.txt<br>
Creates: lstm/<experiment>/time_series/<basins_with_obs>.nc<br>


### Run validation experiments
Evaluate this region with an existing model (e.g., `north-america-mai-v1`):
```
salloc --time=02:00:00 --mem=40G --ntasks=1 --account=def-julemai --gpus-per-node=h100:1 

module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 14_run_validation_experiments.py -s wq-ca-mai -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wq-ca-mai-v1
```

First, set `do_setup = True` in
`14_run_validation_experiments.py`. This can be run on command-line
because it takes just 10 seconds or so. 

Second, set `do_evaluate = True`, `do_merge = True`, and `do_netcdf =
True` and use `submit-cedar-validation_experiments.sh` to submit this
job to cedar/fir. 


### Plot results
Plots results and prints median results on screen (will only show
results if there are observations available for some basins in this project):
```
module load mpi4py/3.1.4
source ~/projects/def-julemai/julemai/env-3.11-cuda/bin/activate
cd /home/julemai/projects/def-julemai/julemai/src

python 15_plot_results_validation_experiments.py -s wq-ca-mai -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31  
```

