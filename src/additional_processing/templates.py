#!/usr/bin/env python
from __future__ import print_function

# Copyright 2023 Juliane Mai - contact[at]juliane-mai[dot]com
#
# License
# This file is part of Juliane Mai's personal code library.
#
# Juliane Mai's personal code library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Juliane Mai's personal code library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with Juliane Mai's personal code library.  If not, see <http://www.gnu.org/licenses/>.
#

"""

Provides templates

License
-------
This file is part of the Basin Fabric which contains scripts to
process data for basins, deriving attributes, processing forcings,
and setting up and training data-driven models.

The Basin Fabric code is free software: you can redistribute it
and/or modify it under the terms of the MIT License.

The Basin Fabric code library is distributed in the hope that it will
be useful,but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
License for more details.

You should have received a copy of the MIT License along with the
Basin Fabric code. If not, see
<https://github.com/julemai/basin-fabric/blob/main/LICENSE>.

Copyright 2023 Juliane Mai - juliane.mai@uwaterloo.ca

History
-------
Written,  JM, Jul 2023

"""




TEMPLATE_NH_CONFIG = '''allow_subsequent_nan_losses: 10
batch_size: {batch_size}
clip_gradient_norm: 1
clip_targets_to_zero:
- qobs_mm_per_day
data_dir: {data_dir}
dataset: generic
device: cuda:0
dynamic_inputs:
- RDRS_v2_A_PR0_SFC_m
- RDRS_v2_P_FB_SFC_W_m2
- RDRS_v2_P_HU_09944_kg_kg
- min_RDRS_v2_P_TT_1.5m_degC
- max_RDRS_v2_P_TT_1.5m_degC
- RDRS_v2_P_UU_10m_kts
- RDRS_v2_P_VV_10m_kts
- RDRS_v2_P_P0_SFC_mb
- potential_evapotranspiration
epochs: {epochs}
experiment_name: {experiment_name}
head: regression
hidden_size: {hidden_size}
initial_forget_bias: 3
learning_rate:
  {learning_rate}
log_n_figures: 0
log_tensorboard: true
loss: NSE
metrics:
- NSE
- KGE
model: cudalstm
num_workers: 4
optimizer: Adam
output_activation: linear
output_dropout: 0.4
predict_last_n: 1
run_dir: None
seed: {seed}
seq_length: 365
static_attributes:
- p_mean
- pet_mean
- aridity
- t_mean
- frac_snow
- high_prec_freq
- high_prec_dur
- low_prec_freq
- low_prec_dur
- Temperate-or-sub-polar-needleleaf-forest
- Temperate-or-sub-polar-broadleaf-deciduous-forest
- Mixed-Forest
- Temperate-or-sub-polar-shrubland
- Temperate-or-sub-polar-grassland
- Wetland
- Cropland
- Barren-Lands
- Urban-and-Built-up
- Water
- mean_elev
- mean_slope
- std_elev
- std_slope
- area_km2
- BD
- CLAY
- GRAV
- OC
- SAND
- SILT
target_variables:
- qobs_mm_per_day
test_basin_file: {test_file}
test_end_date: {end_date}
test_start_date: {start_date}
train_basin_file: {train_file}
train_end_date: {end_date}
train_start_date: {start_date}
validate_every: 3
validate_n_random_basins: 9999
validation_basin_file: {test_file}
validation_end_date: {end_date}
validation_start_date: {start_date}
log_interval: 100
save_validation_results: True
'''
