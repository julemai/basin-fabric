# LSTM experiment: wrtdsk-mai-v1 (only predictions)

This experiment is using the 660 basins in Canada and US where WRTDS-K
was run (basins provided by Juliane Mai) and provides the forcings in
NeuralHydrology format such that trained LSTMs can be used to create
predictions of streamflow for these basins. This dataset is NOT used
to train an LSTM because no or not enough observations of streamflow
are available. 

## Get forcings and observations
```
source env-3.10/bin/activate
python 09_merge_forcings_and_observations.py -s 'wrtdsk-mai'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing' -x wrtdsk-mai-v1
```

Creates: lstm/<experiment>/basins/basins_with_obs.txt<br>
Creates: lstm/<experiment>/basins/basins_without_obs.txt<br>
Creates: lstm/<experiment>/time_series/<basins_with_obs>.nc<br>
