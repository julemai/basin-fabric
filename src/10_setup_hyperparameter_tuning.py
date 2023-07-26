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

# python 10_setup_hyperparameter_tuning.py -s 'grip-gl-mai' -x 'grip-gl-mai-test' -p '2000-01-01;2018-12-31'


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

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')

import pandas as pd
import numpy as np
import datetime as datetime
from templates import TEMPLATE_NH_CONFIG
from raven_common import writeString

case_study   = None
experiment   = 'test'
period       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']. Default: None.")
parser.add_argument('-x', '--experiment', action='store', default=experiment, dest='experiment',
                    help="Name of LSTM experiment . Resulting files will be placed in 'lstm/<experiment>/hyper-parameter-tuning'. Default: 'test'.")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Time period of combined file. Format: YYYY-MM-DD;YYYY-MM-DD. Default: None.")

args         = parser.parse_args()
case_study   = args.case_study
experiment   = args.experiment
period       = args.period

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")
if (period is None):
    raise ValueError("Period (-p) to perform hyper-parameter tuning for must be specified in format YYYY-MM-DD;YYYY-MM-DD.")
if not(period is None):
    try:
        period_start = datetime.datetime.strptime(period.split(';')[0], '%Y-%m-%d')
        period_end   = datetime.datetime.strptime(period.split(';')[1], '%Y-%m-%d')
    except:
        raise ValueError('Period (-p) not formatted as expected. Needs to be "YYYY-MM-DD;YYYY-MM-DD".')

del parser, args







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


# LSTM settings: 675=5*3*3*15 experiments
settings = {
  'learning_rate': [
     {0: 0.0001, 20: 5e-05, 30: 1e-05},
     {0: 0.0005, 20: 0.0001, 30: 5e-05},
     {0: 0.001},
     {0: 0.001, 20: 0.0005, 30: 0.0001},
     {0: 0.005, 10: 0.001, 20: 0.0005},
   ],
   'hidden_size': [ 64, 128, 256 ],
   'batch':  [ 64, 128, 256 ],
   'epochs': [ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 ],
}

# with 3 different seeds
nseeds = 3

# each with 5-fold cross-validation
# - trained on 80% of basins
# - tested/validated on 20% remaining
# create files:
#      train[1-nfolds].txt   --> 80% basins                          (used for "train_basin_file")
#       test[1-nfolds].txt   --> corresponding, remaining 20% basins (used for "test_basin_file" and "validation_basin_file")
nfolds = 5



# create directory for setups
os.makedirs( Path( dir_path ) / '..' / 'lstm' / experiment / 'hyperparam-tuning', exist_ok=True )
os.makedirs( Path( dir_path ) / '..' / 'lstm' / experiment / 'basins' / Path(str(nfolds)+'fold-cv'), exist_ok=True )



# load basins
filename = project_root / '..' / '..' / 'lstm' / experiment / 'basins' / 'basins_with_obs.txt'
if not( filename.exists() ):
    raise ValueError("File containing list of basins not found! Please provide {}.".format(filename))
else:
    basins   = pd.read_csv( filename, header=None, names=['id'] )
    nbasins  = len(basins)
    ntrain   = int( (nfolds-1)*1.0/nfolds * nbasins )   # 80% if nfolds = 5  --> 160 / 200 basins
    ntest    = nbasins - ntrain                         # 20% if nfolds = 5  -->  40 / 200 basins
    nbasins_fold = int( nbasins*1.0 / nfolds )



# create folds: shuffle basins and then split in "nfolds" equally long subsets
basins.sort_values(by=['id'], inplace=True, ignore_index=True)
folds = np.array_split( basins.sample(frac=1).reset_index(drop=True), nfolds )

# write folds to file
for iff,ff in enumerate(folds):

    # sorting indexes
    ff.sort_values(by=['id'], inplace=True, ignore_index=True)

    # write test set to file
    ff.to_csv( Path( dir_path ) / '..' / 'lstm' / experiment / 'basins' / Path(str(nfolds)+'fold-cv') / Path('test'+str(iff+1)+'.txt'),
                   index=False, header=False )

    # get bool array of which basin exists only in "basins" but not in "ff"
    idx_train = basins.merge(ff.drop_duplicates(), on=['id'], how='left', indicator=True)

    # get list of all the train basins
    basins_train = basins[idx_train['_merge'] == 'left_only'].reset_index(drop=True)

    # write train set to file
    basins_train.to_csv( Path( dir_path ) / '..' / 'lstm' / experiment / 'basins' / Path(str(nfolds)+'fold-cv') / Path('train'+str(iff+1)+'.txt'),
                   index=False, header=False )

for seed in range(1,nseeds+1):
    counter = 0
    for learning_rate in settings['learning_rate']:
        for hidden_size in settings['hidden_size']:
            for batch in settings['batch']:
                for epochs in settings['epochs']:
                    for fold in range(1,nfolds+1):

                        counter += 1

                        # format learning rate
                        learning_rate = '\n  '.join([ ii.strip() for ii in str(learning_rate).replace('{','').replace('}','').split(',') ])
                        learning_rate_str = learning_rate.replace(': 0.','').replace('\n  ','-').replace(': ','')

                        # format dates
                        start_date = period_start.strftime("%Y/%m/%d")
                        end_date = period_end.strftime("%Y/%m/%d")

                        # get name of experiment
                        # gripGL-hyperparam-tuning_learning_rate0001_hidden_size128_batch_size256_seed3_fold2
                        experiment_name = f'{experiment}_learning_rate{learning_rate_str}_hidden_size{hidden_size}_batch{batch}_seed{seed}_fold{fold}'

                        # get data directory
                        data_dir = str( Path( project_root / '..' / '..' / 'lstm' / experiment ) )

                        # get names of test and train file
                        test_file  = str( Path('basins') / Path(str(nfolds)+'fold-cv') / Path('test'+str(fold)+'.txt') )
                        train_file = str( Path('basins') / Path(str(nfolds)+'fold-cv') / Path('train'+str(fold)+'.txt') )

                        template = TEMPLATE_NH_CONFIG.format(
                            experiment_name=experiment_name,
                            data_dir=data_dir,
                            learning_rate=learning_rate,
                            hidden_size=hidden_size,
                            batch=batch,
                            epochs=epochs,
                            seed=seed,
                            test_file=test_file,
                            train_file=train_file,
                            start_date=start_date,
                            end_date=end_date,
                            )
                        filename = Path( dir_path ) / '..' / 'lstm' / experiment / 'hyperparam-tuning' / 'cfg' / 'config_{:d}_{:04d}.yml'.format(seed,counter)
                        writeString( filename, template)
