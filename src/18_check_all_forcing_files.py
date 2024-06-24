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


# # checks min/max of all forcing files regions/<region>/forcings/<basin>/*_lp_daily_local.nc
# # needs to run after "08_static_attributes_forcings.py" which creates the "*_lp_daily_local.nc" files.

# python 18_check_all_forcing_files.py -s 'lake-erie-us-gaffney' -f 'rdrs-v2.1_north-america'
# python 18_check_all_forcing_files.py -s 'conus-zhi'            -f 'rdrs-v2.1_north-america'
# python 18_check_all_forcing_files.py -s 'north-america-mai'    -f 'rdrs-v2.1_north-america'     # does forcing file
# python 18_check_all_forcing_files.py -s 'north-america-mai-v1' -f 'rdrs-v2.1_north-america'     # does LSTM time_series file


"""

Prints out all forcing files and variables where global minimum of variable or global maximum of 
variable is below/above a threshold which is indicating a problem in the production of the files.

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
Written,  JM, Jun 2024

"""


# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')
sys.path.append(dir_path+'/lib')

import pandas   as pd
import xarray   as xr
import numpy    as np
import glob     as glob
import time     as time

case_study   = None
forcing      = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Check variables in forcing files. Prints variables that are outside of a certain bound indicating problems with the file.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']. Default: None.")
parser.add_argument('-f', '--forcing', action='store', default=forcing, dest='forcing',
                    help="Forcing type needs to be specified. E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")

args         = parser.parse_args()
case_study   = args.case_study
forcing      = args.forcing

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']")
if (forcing is None):
    raise ValueError("Forcing type (-f) must be specified.E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")

del parser, args

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')



t1 = time.time()

do_forcing = True
project_root = Path(dir_path,'..','regions',case_study,'forcings')
filenames = np.sort(glob.glob(str(Path(project_root,'*','*_agg_'+forcing+'_lp_daily_local.nc'))))

if len(filenames) == 0:
    do_forcing = True
    filenames = np.sort(glob.glob(str(Path(project_root,'*','*_agg_'+forcing+'_lp.nc'))))

if len(filenames) == 0:
    do_forcing = False
    project_root = Path(dir_path,'..','lstm',case_study,'time_series')
    filenames = np.sort(glob.glob(str(Path(project_root,'*.nc'))))

found_outlier = False
for filename in filenames:

    if do_forcing:
        basin = filename.split('/')[-2]
    else:
        basin = filename.split('/')[-1].split('.')[0]
    print("Checking basin: {}  --> {}".format(basin,filename))

    data = xr.open_dataset(filename)
    variables = list(data.keys())

    for variable in variables:

        val_min = data[variable].min().values.item()
        val_max = data[variable].max().values.item()
        if val_min < -99999. or val_max > 99999.:

             # find indexes with large data
            idx = np.where(np.abs(data[variable])>99999.)[0]

            # find date range of those data
            start_date = str(np.array(data['date'][idx[ 0]])).split('T')[0]
            end_date   = str(np.array(data['date'][idx[-1]])).split('T')[0]
            
            print("{}: {} with value range [{},{}] looks suspicious. Suspicious dates range from {} to {}.".format(filename,variable,val_min,val_max,start_date,end_date))

            found_outlier = True

if not(found_outlier):
    print('No outliers/missing values found in any of the {} forcing files analysed.'.format(len(filenames)))



