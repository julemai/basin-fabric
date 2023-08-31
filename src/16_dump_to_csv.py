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


# dump netcdf file to CSV files (per basin)

# python 16_dump_to_csv.py -i ../regions/wisconsin-lewis/predictions/using_grip-gl-mai-v2/ensemble/test_ensemble_results.nc      -o ../regions/wisconsin-lewis/predictions/using_grip-gl-mai-v2/ensemble/csv/
# python 16_dump_to_csv.py -i ../regions/lake-erie-us-gaffney/predictions/using_grip-gl-mai-v2/ensemble/test_ensemble_results.nc -o ../regions/lake-erie-us-gaffney/predictions/using_grip-gl-mai-v2/ensemble/csv/

"""

Dumps content of NetCDF file to CSV files. Expects variables:
- qobs_m3_per_s_obs(basin, datetime)
- qobs_m3_per_s_sim(basin, datetime)
- basin(basin)
- datetime(datetime)

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
# General settings
#


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
# import numpy    as np
# import glob     as glob
# import time     as time
# import datetime as datetime
# import json     as json
# import color                            # in lib/
# from brewer        import get_brewer    # in lib/
# from position      import position      # in lib/
# from str2tex       import str2tex       # in lib/
# from abc2plot      import abc2plot      # in lib/
# from autostring    import astr          # in lib/
# from errormeasures import nse, kge, rmse, mse, mae, pear2, bias   # in lib/

input_file    = None
output_folder = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-i', '--input_file', action='store', default=input_file, dest='input_file',
                    help="Input NetCDF file. Default: None.")
parser.add_argument('-o', '--output_folder', action='store', default=output_folder, dest='output_folder',
                    help="Name of folder to dump CSV files into. Folder dwill be created if it doesnt exist. Default: None.")

args         = parser.parse_args()
input_file    = args.input_file
output_folder = args.output_folder

if (input_file is None):
    raise ValueError("Input file needs to be specified.")

if (output_folder is None):
    raise ValueError("Output folder needs to be specified.")

if not os.path.exists(input_file):
    raise ValueError("Input file {} does not exist.".format(input_file))

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

del parser, args


# read file
ds = xr.open_dataset(input_file)

# basin names
basins = ds['basin'].data

for basin in basins:

    # select only current basin
    ids = ds.sel({'basin':basin})

    # convert to pandas dataframe
    idf = ids.to_dataframe()

    # drop unneccessary column
    idf = idf.drop(['basin'], axis=1)

    # rename column
    idf = idf.rename(columns={"qobs_m3_per_s_obs": "qobs_m3_per_s", "qobs_m3_per_s_sim": "qsim_m3_per_s"})

    # filename
    filename_out = Path(output_folder+'/streamflow_'+str(basin)+'.csv')

    # dump to csv
    idf.to_csv(filename_out)

    # report
    print('Wrote: {}'.format(filename_out))
