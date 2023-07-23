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

# source env-3.10/bin/activate
# pyenv activate env-3.8.5-basin-fabric

# python 08_static_attributes_forcings.py -s 'wisconsin-lewis'     -f 'rdrs-v2.1_north-america' -p 'all'
# python 08_static_attributes_forcings.py -s 'conus-zhi' -f 'rdrs-v2.1_north-america' -p 'all'
# python 08_static_attributes_forcings.py -s 'ontario-zhi'   -f 'rdrs-v2.1_north-america' -p 'all'
# python 08_static_attributes_forcings.py -s 'grip-gl-mai'       -f 'rdrs-v2.1_north-america' -p 'all'


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
Written,  MG, Jan 2022
Modified, JM, Jun 2023 - modify from ipynb to python script

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
import datetime
from pathlib import Path

case_study   = None
forcing      = None
period       = 'all'

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai'].")
parser.add_argument('-f', '--forcing', action='store', default=forcing, dest='forcing',
                    help="Forcing type needs to be specified. E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Time period to evaluate attributes for. Format: YYYY-MM-DD_HH:MM:SS;YYYY-MM-DD_HH:MM:SS. The two timesteps need to exist in NetCDF file. Default: all")

args         = parser.parse_args()
case_study   = args.case_study
forcing      = args.forcing
period       = args.period

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")
if (forcing is None):
    raise ValueError("Forcing type (-f) must be specified.E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")
if (period != 'all'):
    try:
        period_start = datetime.datetime.strptime(period.split(';')[0], '%Y-%m-%d_%H:%M:%S')
        period_end   = datetime.datetime.strptime(period.split(';')[1], '%Y-%m-%d_%H:%M:%S')
    except:
        raise ValueError('Period (-p) not formatted as expected. Needs to be "YYYY-MM-DD_HH:MM:SS;YYYY-MM-DD_HH:MM:SS".')

del parser, args

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')


from pathlib import Path
from datetime import datetime
from get_time_zone import get_time_zone # in additional_processing

import numpy as np
import pandas as pd
import xarray as xr

from neuralhydrology.datautils.utils import load_basin_file
from neuralhydrology.datautils.climateindices import calculate_dyn_climate_indices
from neuralhydrology.datautils.pet import get_priestley_taylor_pet


if case_study == 'wisconsin-lewis':
    project_root = Path(dir_path+'/../regions/wisconsin-lewis')

elif case_study == 'ontario-zhi':
    project_root = Path(dir_path+'/../regions/ontario-zhi')

elif case_study == 'conus-zhi':
    project_root = Path(dir_path+'/../regions/conus-zhi')

elif case_study == 'grip-gl-mai':
    project_root = Path(dir_path+'/../regions/grip-gl-mai')

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))



if forcing == 'rdrs-v2.1_north-america':
    var_precip  = 'RDRS_v2.1_A_PR0_SFC'   # precipitation (primary)
    var_precip2 = 'RDRS_v2.1_P_PR0_SFC'   # precipitation (secondary); set to None is not existing
    var_temp    = 'RDRS_v2.1_P_TT_1.5m'   # temperature
    var_swrad   = 'RDRS_v2.1_P_FB_SFC'    # shortwave radiation
elif forcing == 'rdrs-v2_grip-gl':
    var_precip  = 'RDRS_v2_A_PR0_SFC'   # precipitation (primary)
    var_precip2 = None                  # precipitation (secondary); set to None is not existing
    var_temp    = 'RDRS_v2_P_TT_1.5m'   # temperature
    var_swrad   = 'RDRS_v2_P_FB_SFC'    # shortwave radiation
else:
    raise ValueError('Forcing details not known for this forcing. Please specify.')





do_forcings       = True



if do_forcings:

    # load static attributes
    static_attributes_basin   = pd.read_csv(project_root / 'basins.csv', index_col=[0],
                                                dtype={'id': 'str', 'name': 'str', 'lat': 'float', 'lon': 'float'})
    static_attributes_geophys = pd.read_csv(project_root / 'attributes' / 'static_attributes.csv', index_col=[0],
                                                dtype={'basin':'str'})

    clim_indices = {}

    no_forcing_basins = []
    no_discharge_basins  = []
    nbasins = len(static_attributes_basin.index)
    for ibasin,basin in enumerate(sorted(static_attributes_basin.index)):

        basin_forcing_file = project_root / 'forcings' / f'{basin}' / f'{basin}_agg_{forcing}_lp.nc'
        if not basin_forcing_file.exists():
            no_forcing_basins.append(basin)
            print("File not found for basin {}: {}".format(basin,basin_forcing_file))
            continue

        lat = static_attributes_basin.loc[basin, 'lat']
        lon = static_attributes_basin.loc[basin, 'lon']

        # get time shift
        timezone_offset_hrs = get_time_zone(lat,lon)
        # print("Shift time: UTC{}h".format(timezone_offset_hrs))

        # read data
        xr_forcings = xr.open_dataset(basin_forcing_file)

        # save all attributes for later
        vars_in_ori = list(xr_forcings.variables)
        attributes_ori = {}
        for vv in vars_in_ori:
            attributes_ori[vv] = xr_forcings[vv].attrs

        forcings = xr_forcings.to_dataframe()
        forcings.index.name = 'time'
        forcings = forcings.reset_index(level='nHRU')   # nHRU is an index column --> make regular column
        forcings = forcings.drop(['nHRU'], axis=1)      # remove nHRU column entirely (is 0 everywhere anyway in lumped forcings)

        # shift time
        # print("forcings before: ",forcings)
        forcings = forcings.shift(timezone_offset_hrs, freq='H')
        # print("forcings after: ",forcings)

        climidx_forcings = forcings
        if period != 'all':
            climidx_forcings = climidx_forcings.loc[period_start:period_end]
            assert np.all(climidx_forcings.index[[0,-1]] == pd.DatetimeIndex([str(period_start), str(period_end)]))

        if forcings.isna().all(axis=None):
            no_forcing_basins.append(basin)
            continue

        # resample to daily values: sum(precip), min/max(temp), mean for all other variables
        # run once with calibration data (for climate index calculation), once with full data (for actual forcings)
        for ii, forcing_set in enumerate([climidx_forcings, forcings]):
            daily_resampled = forcing_set.resample('1D')
            daily_forcings = daily_resampled.mean()

            # precip
            daily_forcings[var_precip]  = daily_resampled[var_precip].sum(min_count=1)
            if not(var_precip2 is None):
                daily_forcings[var_precip2] = daily_resampled[var_precip2].sum(min_count=1)
            # temp
            daily_forcings[var_temp+'_min'] = daily_resampled[var_temp].min()
            daily_forcings[var_temp+'_max'] = daily_resampled[var_temp].max()
            daily_forcings['potential_evapotranspiration'] = \
                get_priestley_taylor_pet(daily_forcings[var_temp+'_min'].values,
                                         daily_forcings[var_temp+'_max'].values,
                                         daily_forcings[var_swrad].values,
                                         lat=lat,
                                         elev=static_attributes_geophys.loc[basin, 'mean_elev'],
                                         doy=daily_forcings.index.dayofyear.values)

            if ii == 0:
                # since window_length is length of forcings, there will only be one date returned, so we can do .iloc[0]
                if attributes_ori[var_precip]['units'] == 'm':
                    mult = 1000. # m to mm
                elif attributes_ori[var_precip]['units'] == 'mm':
                    mult = 1. # mm to mm
                else:
                    raise ValueError('Unit for precipitation not known. Please implement conversion factor to get [mm].')
                clim_indices[basin] = calculate_dyn_climate_indices(daily_forcings[var_precip] * mult,
                                                                       daily_forcings[var_temp+'_max'],
                                                                       daily_forcings[var_temp+'_min'],
                                                                       daily_forcings['potential_evapotranspiration'],
                                                                       window_length=len(daily_forcings)).iloc[0]

        # # add discharge
        # discharge = load_grip_discharge(basin)
        # daily_forcings['qobs_mm_per_day'] = discharge if discharge is not None else np.nan
        # if discharge is None:
        #     no_discharge_basins.append(basin)

        # replace original data (hourly) with resampled (daily) and save as NetCDF
        xr_forcings['time'] = forcings.index  # shift time
        xr_forcings         = xr_forcings.resample(time='1D').pad()  # make daily (especially time variable and dimension)

        variables = list(daily_forcings.columns)
        for vv in variables:

            # set values
            if vv != 'time':
                xr_forcings[vv] = daily_forcings[vv]

            # set attributes
            if vv in vars_in_ori:
                xr_forcings[vv].attrs = attributes_ori[vv]
            elif vv == var_temp+'_max':
                xr_forcings[vv].attrs = attributes_ori[var_temp]
                xr_forcings[vv].attrs['long_name'] = attributes_ori[var_temp]['long_name']+' (maximum)'
            elif vv == var_temp+'_min':
                xr_forcings[vv].attrs = attributes_ori[var_temp]
                xr_forcings[vv].attrs['long_name'] = attributes_ori[var_temp]['long_name']+' (minimum)'
            elif vv == 'potential_evapotranspiration':
                attrs = {
                    'long_name': 'Potential evapotranspiration based on Priestley-Taylor using get_priestley_taylor_pet() of NeuralHydrology',
                    'coordinates': 'lon lat',
                    'grid_mapping': 'rotated_pole',
                    'cell_methods': 'time: mean',
                    'units': 'mm/day',
                    }
                xr_forcings[vv].attrs = attrs

        # rename time --> date
        xr_forcings = xr_forcings.rename_dims({'time':'date'})
        xr_forcings = xr_forcings.rename_vars({'time':'date'})

        # ds = xr.Dataset.from_dataframe(daily_forcings)
        filename = project_root / 'forcings' / f'{basin}' / f'{basin}_agg_{forcing}_lp_daily_local.nc'
        xr_forcings.to_netcdf( filename )
        print('Wrote: {} (basin {} of {})'.format(filename,ibasin+1,nbasins))

    print(f'\nNo forcings for basins:  ({len(no_forcing_basins)}) {no_forcing_basins}')
    # print(f'No discharge for basins: ({len(no_discharge_basins)}) {no_discharge_basins}')

    # print('clim_indices = {}'.format(clim_indices))

# ---------------------------------------------------------------


# merge information collected

static_attrs = clim_indices

static_attrs = pd.DataFrame(clim_indices).T
static_attrs.index.set_names('basin', inplace=True)
static_attrs.columns = [col.split('_dyn')[0] for col in static_attrs.columns]
filename_out = Path(project_root / 'attributes' / 'climate_indices.csv')
static_attrs.to_csv(filename_out)

print('\nSaved information to: {}'.format(filename_out))
