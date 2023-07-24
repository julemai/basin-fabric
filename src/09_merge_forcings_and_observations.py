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

# python 09_merge_forcings_and_observations.py -s 'wisconsin-lewis'  -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing'  -x test
# python 09_merge_forcings_and_observations.py -s 'conus-zhi'        -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing'  -x test
# python 09_merge_forcings_and_observations.py -s 'ontario-zhi'      -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing'  -x test
# python 09_merge_forcings_and_observations.py -s 'grip-gl-mai'      -f 'rdrs-v2.1_north-america' -o 'daily_streamflow.nc' -p 'forcing'  -x test

"""

Merges forcings with observations into new file (used to train LSTM then).

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

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

case_study   = None
forcing      = None
observation  = None
period       = 'forcing'
experiment   = 'test'

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']. Default: None.")
parser.add_argument('-f', '--forcing', action='store', default=forcing, dest='forcing',
                    help="Forcing type needs to be specified. E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp_daily_local.nc'. Default: None.")
parser.add_argument('-o', '--observation', action='store', default=observation, dest='observation',
                    help="File to use for observations. Needs to be located in:  'regions/<case_study>/observations/'. Default: None.")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Time period of combined file. Format: YYYY-MM-DD_HH:MM:SS;YYYY-MM-DD_HH:MM:SS. Default: 'forcing' (i.e., time period in forcing files)")
parser.add_argument('-x', '--experiment', action='store', default=experiment, dest='experiment',
                    help="Name of LSTM experiment this forcing-observation combination will be used for. Resulting files will be placed in 'lstm/<experiment>/time_series/<basin>.nc'. Default: 'test'.")



args         = parser.parse_args()
case_study   = args.case_study
forcing      = args.forcing
observation  = args.observation
period       = args.period
experiment   = args.experiment


if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")
if (forcing is None):
    raise ValueError("Forcing type (-f) must be specified.E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")
if (observation is None):
    raise ValueError("Observation file (-o) must be specified.E.g., 'daily_streamflow.nc']. These files need to be available in: 'regions/<case_study>/observations/'.")
if (period != 'forcing'):
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

import numpy as np
import pandas as pd
import xarray as xr


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


# load streamflow data
streamflow = xr.open_dataset(project_root / f'observations/daily_streamflow.nc')



def load_streamflow(basin: str, station:str) -> pd.Series:

    # basin   ... basin where we have attributes for (can also be named after a nutrient station or lake, etc)
    # station ... gauge station ID

    # make sure these are strings and not byte
    station_ids = np.array(streamflow['station_id'], dtype=np.unicode_)

    if station in list(station_ids):
        nstation = np.where(station_ids == station)[0][0]
        istreamflow = streamflow.sel(nstations=nstation)['Q'].to_series()
        area = static_attributes_geophys.loc[basin, 'area_km2'] * 1000_000  # km2 to m2
        istreamflow.loc[istreamflow < 0] = np.nan
        istreamflow.index.name = 'date'

        return istreamflow * (60 * 60 * 24) * 1000.0 / area  # m3/s to mm/day
    else:
        return None





# load static attributes
static_attributes_basin   = pd.read_csv(project_root / 'basins.csv', index_col=[0],
                                            dtype={'id': 'str', 'name': 'str', 'lat': 'float', 'lon': 'float', 'obs_q': 'str'})
static_attributes_geophys = pd.read_csv(project_root / 'attributes' / 'static_attributes.csv', index_col=[0],
                                            dtype={'basin':'str'})


no_forcing_basins = []
no_streamflow_basins  = []
streamflow_basins = []
nbasins = len(static_attributes_basin.index)
for ibasin,basin in enumerate(sorted(static_attributes_basin.index)):

    basin_forcing_file = project_root / 'forcings' / f'{basin}' / f'{basin}_agg_{forcing}_lp_daily_local.nc'
    if not basin_forcing_file.exists():
        no_forcing_basins.append(basin)
        print("File not found for basin {}: {}".format(basin,basin_forcing_file))
        continue

    lat      = static_attributes_basin.loc[basin, 'lat']
    lon      = static_attributes_basin.loc[basin, 'lon']
    obs_q_id = static_attributes_basin.loc[basin, 'obs_q']
    area     = static_attributes_geophys.loc[basin, 'area_km2']


    # read forcing data
    xr_forcings = xr.open_dataset(basin_forcing_file)

    # save all attributes for later
    vars_in_ori = list(xr_forcings.variables)
    attributes_ori = {}
    for vv in vars_in_ori:
        attributes_ori[vv] = xr_forcings[vv].attrs

    forcings = xr_forcings.to_dataframe()
    forcings.index.name = 'date'

    # clip to requested period
    if period != 'forcing':
        forcings = forcings.loc[period_start:period_end]
        assert np.all(forcings.index[[0,-1]] == pd.DatetimeIndex([str(period_start), str(period_end)]))

    if forcings.isna().all(axis=None):
        no_forcing_basins.append(basin)
        continue


    # read streamflow
    streamflow_basin = load_streamflow(basin=basin, station=obs_q_id)

    # add streamflow
    if streamflow_basin is None:
        forcings['qobs_mm_per_day'] = np.nan
        no_streamflow_basins.append(basin)
        continue # skipping writing of file
    else:
        forcings['qobs_mm_per_day'] = streamflow_basin
        streamflow_basins.append(basin)

    # write file (if streamflow was found)
    variables = list(forcings.columns)
    for vv in variables:

        # set values
        if vv != 'date':
            xr_forcings[vv] = forcings[vv]

        # set attributes
        if vv in vars_in_ori:
            xr_forcings[vv].attrs = attributes_ori[vv]
        elif vv == 'qobs_mm_per_day':
            attrs = {
                'long_name': 'Observed streamflow',
                'coordinates': 'lon lat',
                'grid_mapping': 'rotated_pole',
                'cell_methods': 'time: mean',
                'units': 'mm/day',
                }
            xr_forcings[vv].attrs = attrs

    # rename time --> date
    #xr_forcings = xr_forcings.rename_dims({'time':'date'})
    #xr_forcings = xr_forcings.rename_vars({'time':'date'})

    # ds = xr.Dataset.from_dataframe(daily_forcings)
    filename = project_root / '../..' / 'lstm' / f'{experiment}' / 'time_series' / f'{basin}.nc'
    os.makedirs( Path(filename).parent, exist_ok=True )
    xr_forcings.to_netcdf( filename )
    print('Wrote: {} (basin {} of {})'.format(filename,ibasin+1,nbasins))


print(f'\nNo forcings for basins:  ({len(no_forcing_basins)}) {no_forcing_basins}')
print(f'No streamflow for basins: ({len(no_streamflow_basins)}) {no_streamflow_basins}')


# write basin lists
filename_with_obs    = project_root / '../..' / 'lstm' / f'{experiment}' / 'basins' / f'basins_with_obs.txt'
filename_without_obs = project_root / '../..' / 'lstm' / f'{experiment}' / 'basins' / f'basins_without_obs.txt'

os.makedirs( Path(filename_with_obs).parent, exist_ok=True )

with open(filename_with_obs, 'w') as ff:
    for basin in streamflow_basins:
        ff.write(f"{basin}\n")

with open(filename_without_obs, 'w') as ff:
    for basin in no_streamflow_basins:
        ff.write(f"{basin}\n")
