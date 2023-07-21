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

# pyenv activate env-3.8.5-basin-fabric
# python 04_retrieve_observations.py -s Wisconsin -p 1980-01-01:2018-12-31
# python 04_retrieve_observations.py -s GRIP-GL   -p 1980-01-01:2018-12-31
# python 04_retrieve_observations.py -s Wisconsin -p 1980-01-01:2018-12-31
# python 04_retrieve_observations.py -s Wisconsin -p 1980-01-01:2018-12-31

"""

Retrieves observations for basins listed in <region>/basins.csv columns for
'obs_q', 'obs_n', or 'obs_p'.


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
Written,  JM, Jul 2023 - using read_streamflow() and read_concentration() from
PWQMN-portal as base for Hydat and adding logic for USGS data retrieval.

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

case_study   = None
period       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Retrieve observations.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['Wisconsin', 'Great-Lakes', 'North-America', 'GRIP-GL'].")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Period to retrieve data for. Format: YYYY-MM-DD:YYYY-MM-DD. Default: None (=all data found).")

args         = parser.parse_args()
case_study   = args.case_study
period       = args.period

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['Wisconsin', 'Great-Lakes', 'North-America', 'GRIP-GL']")

del parser, args



# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import fiona
from fiona import transform
import rasterio as rio
from rasterio import mask
import re

from b2_read_streamflow import get_info_station
from b2_read_streamflow import read_streamflow
from b3_write_streamflow import write_streamflow_nc


if case_study == 'Wisconsin':
    project_root = Path(dir_path+'/../regions/Wisconsin_waterheds')  #Path('/publicwork/gauch/GRIP-GL/scripts/MachineLearning')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'Great-Lakes':
    project_root = Path(dir_path+'/../regions/Great_Lakes_watersheds')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'North-America':
    project_root = Path(dir_path+'/../regions/North_America_watersheds/')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'GRIP-GL':
    project_root = Path(dir_path+'/../regions/GRIP-GL/')
    types = ['shapefiles']
    filepattern = '*/*.shp'

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))

if not(period is None):
    period = {'start':period.split(':')[0], 'end':period.split(':')[1]}


# find list of basins
static_attributes_basin   = pd.read_csv(project_root / 'basins.csv', index_col=[0],
                                        dtype={'id': 'str', 'name': 'str', 'lat': 'float', 'lon': 'float', 'obs_q': 'str'})

obs_q = static_attributes_basin['obs_q'].values

obs_q_CA = []
obs_q_US = []
obs_q_UNKNOWN = []
for iobs_q in obs_q:
    if ( str(iobs_q) != 'nan' ):

        pattern_CA = re.compile("^([0-9][0-9][A-Z][A-Z][0-9]+)+$")
        pattern_US = re.compile("^([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]+)+$")

        if pattern_CA.match(iobs_q):
            #print("{} is Canadian".format(iobs_q))
            obs_q_CA.append(iobs_q)
        elif pattern_US.match(iobs_q):
            #print("{} is American".format(iobs_q))
            obs_q_US.append(iobs_q)
        else:
            #print("{} is UNKNOWN".format(iobs_q))
            obs_q_UNKNOWN.append(iobs_q)

info_streamflow = {}
data_streamflow = {}

print('No pattern found for following stations: {}'.format(obs_q_UNKNOWN))

# retrieve data from USGS (data downloaded on the fly; requires internet connection)
if len(obs_q_US) > 0:

    print('Retrieving data from USGS for {} US stations ... '.format(len(obs_q_US)))
    source    = 'usgs'
    filename  = None
    station   = ','.join(obs_q_US)
    pairsfile = None

    info_streamflow_US = get_info_station(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)
    data_streamflow_US = read_streamflow( source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

    info_streamflow.update( info_streamflow_US )
    data_streamflow.update( data_streamflow_US )

# retrieve data from HYDAT (read from data/observations/streamflow/Hydat.sqlite3 (pre-downloaded); requires no internet connection)
if len(obs_q_CA) > 0:

    print('Retrieving data from HYDAT for {} CA stations ... '.format(len(obs_q_CA)))
    source    = 'hydat'
    filename  = '../data/observations/streamflow/Hydat.sqlite3'
    station   = ','.join(obs_q_CA)
    pairsfile = None

    info_streamflow_CA = get_info_station(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)
    data_streamflow_CA = read_streamflow( source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

    info_streamflow.update( info_streamflow_CA )
    data_streamflow.update( data_streamflow_CA )


# write all to NetCDF
print('Write to NetCDF ... ')
outfolder = project_root / 'observations'
os.makedirs( Path(outfolder), exist_ok=True )

filename     = str( outfolder / 'daily_streamflow.nc' )

filenames_streamflow = write_streamflow_nc(info_dict=info_streamflow,
                                               data_dict=data_streamflow,
                                               filename=filename,
                                               write_symbol=False,
                                               nodata=np.nan,
                                               station=None,
                                               period=period,
                                               silent=True)


print('Saved information to: {}'.format(filename))
