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

# pyenv activate env-3.8.5-neuralhydrology


"""

Derives static basin attributes from forcings (9).

    p_mean
    pet_mean
	aridity
	t_mean
	frac_snow
	high_prec_freq
	high_prec_dur
	low_prec_freq
	low_prec_dur



History
-------
Written,  MG, Jan 2022
Modified, JM, Jun 2023 - modify from ipynb to python script

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

case_study   = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['Wisconsin', 'Great-Lakes', 'North-America', 'GRIP-GL'].")

args         = parser.parse_args()
case_study   = args.case_study

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['Wisconsin', 'Great-Lakes', 'North-America', 'GRIP-GL']")

del parser, args




from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import xarray as xr

from neuralhydrology.datautils.utils import load_basin_file
from neuralhydrology.datautils.climateindices import calculate_dyn_climate_indices
from neuralhydrology.datautils.pet import get_priestley_taylor_pet


if case_study == 'Wisconsin':
    project_root = Path('/Users/j6mai/Documents/Nandita/Wisconsin_waterheds')  #Path('/publicwork/gauch/GRIP-GL/scripts/MachineLearning')

elif case_study == 'Great-Lakes':
    project_root = Path('/Users/j6mai/Documents/Nandita/Great_Lakes_watersheds')

elif case_study == 'North-America':
    project_root = Path('/Users/j6mai/Documents/Nandita/North_America_watersheds/')

elif case_study == 'GRIP-GL':
    project_root = Path('/Users/j6mai/Documents/GitHub/GRIP-GL/data/shapefiles/great-lakes/')

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))




do_forcings       = True



if do_forcings:

    clim_indices = {}

    no_forcing_basins = []
    no_discharge_basins  = []
    for basin in tqdm(sorted(static_attributes.index)):

        is_spatial_val = False
        basin_rdrsv2_file = project_root / '../../data/ml-met-calibration' / f'ml_met_{basin}.csv'
        val_basin_rdrsv2_file = project_root / '../../data/ml-met-validation-temporal' / f'ml_met_{basin}.csv'
        if not basin_rdrsv2_file.exists():
            is_spatial_val = True
            basin_rdrsv2_file = project_root / '../../data/ml-met-validation-spatial' / f'ml_met_{basin}.csv'
            if not basin_rdrsv2_file.exists():
                no_forcings_basins.append(basin)
                continue

        # The aggregated RDRS forcings are already in local standard time (UTC-5)
        if not is_spatial_val:
            # don't use validation data to calculate climate indices
            climidx_forcings = pd.read_csv(basin_rdrsv2_file, index_col=0, parse_dates=[0], skipinitialspace=True)
            climidx_forcings.index.name = 'date'
            # temporal validation forcings also contain the calibration date range
            forcings = pd.read_csv(val_basin_rdrsv2_file, index_col=0, parse_dates=[0], skipinitialspace=True)
            forcings.index.name = 'date'
        else:
            forcings = pd.read_csv(basin_rdrsv2_file, index_col=0, parse_dates=[0], skipinitialspace=True)
            forcings.index.name = 'date'
            climidx_forcings = forcings
            climidx_forcings = climidx_forcings.loc[:'2011-01-01 07:00:00']

        assert np.all(climidx_forcings.index[[0,-1]] == pd.DatetimeIndex(['2000-01-01 08:00:00', '2011-01-01 07:00:00']))

        if forcings.isna().all(axis=None):
            no_forcing_basins.append(basin)
            continue

        lat = static_attributes.loc[basin, 'gauge_lat']

        # resample to daily values: sum(precip), min/max(temp), mean for all other variables
        # run once with calibration data (for climate index calculation), once with full data (for actual forcings)
        for i, forcing_set in enumerate([climidx_forcings, forcings]):
            daily_resampled = forcing_set.resample('1D')
            daily_forcings = daily_resampled.mean()

            # precip
            daily_forcings['RDRS_v2_A_PR0_SFC_m'] = daily_resampled['RDRS_v2_A_PR0_SFC_m'].sum(min_count=1)
            # temp
            daily_forcings['min_RDRS_v2_P_TT_1.5m_degC'] = daily_resampled['RDRS_v2_P_TT_1.5m_degC'].min()
            daily_forcings['max_RDRS_v2_P_TT_1.5m_degC'] = daily_resampled['RDRS_v2_P_TT_1.5m_degC'].max()
            daily_forcings['potential_evapotranspiration'] = \
                get_priestley_taylor_pet(daily_forcings['min_RDRS_v2_P_TT_1.5m_degC'].values,
                                         daily_forcings['max_RDRS_v2_P_TT_1.5m_degC'].values,
                                         daily_forcings['RDRS_v2_P_FB_SFC_W_m2'].values,  # shortwave radiation
                                         lat=lat,
                                         elev=static_attributes.loc[basin, 'mean_elev'],
                                         doy=daily_forcings.index.dayofyear.values)

            if i == 0:
                # since window_length is length of forcings, there will only be one date returned, so we can do .iloc[0]
                clim_indices[basin] = calculate_dyn_climate_indices(daily_forcings['RDRS_v2_A_PR0_SFC_m'] * 1000,  # m to mm
                                                                       daily_forcings['max_RDRS_v2_P_TT_1.5m_degC'],
                                                                       daily_forcings['min_RDRS_v2_P_TT_1.5m_degC'],
                                                                       daily_forcings['potential_evapotranspiration'],
                                                                       window_length=len(daily_forcings)).iloc[0]

        # # add discharge
        # discharge = load_grip_discharge(basin)
        # daily_forcings['qobs_mm_per_day'] = discharge if discharge is not None else np.nan
        # if discharge is None:
        #     no_discharge_basins.append(basin)

        # xr_forcings_and_discharge = xr.Dataset.from_dataframe(daily_forcings)
        # xr_forcings_and_discharge.to_netcdf(project_root / 'time_series' / f'{basin}.nc')

    print(f'No forcings for basins:  ({len(no_forcing_basins)}) {no_forcing_basins}')
    # print(f'No discharge for basins: ({len(no_discharge_basins)}) {no_discharge_basins}')

    print('clim_indices = {}'.format(clim_indices))

# ---------------------------------------------------------------


# merge information collected

static_attrs = clim_indices

static_attrs.index.set_names('basin', inplace=True)
filename_out = Path(project_root / 'attributes' / 'static_attributes_forcings_{}.csv'.format(case_study))
static_attrs.to_csv(filename_out)

print('Saved information to: {}'.format(filename_out))
