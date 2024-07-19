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

# source /scratch/julemai/basin-fabric/env-cuda/bin/activate

# evaluate wisconsin-lewis using trained various LSTMs
# python 14_run_validation_experiments.py -s wisconsin-lewis -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
# python 14_run_validation_experiments.py -s wisconsin-lewis -u conus-zhi-v2    -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
# python 14_run_validation_experiments.py -s wisconsin-lewis -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1

# evaluate ontario-zhi using trained various LSTMs
# python 14_run_validation_experiments.py -s ontario-zhi     -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
# python 14_run_validation_experiments.py -s ontario-zhi     -u conus-zhi-v2    -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
# python 14_run_validation_experiments.py -s ontario-zhi     -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1

# evaluate conus-zhi using trained various LSTMs
# python 14_run_validation_experiments.py -s conus-zhi     -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f conus-zhi-v1
# python 14_run_validation_experiments.py -s conus-zhi     -u conus-zhi-v2    -p 1980-01-01:2018-12-31 -f conus-zhi-v2
# python 14_run_validation_experiments.py -s conus-zhi     -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f conus-zhi-v1

# evaluate grip-gl-mai using trained various LSTMs
# python 14_run_validation_experiments.py -s grip-gl-mai   -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f grip-gl-mai-v2
# python 14_run_validation_experiments.py -s grip-gl-mai   -u conus-zhi-v2    -p 1980-01-01:2018-12-31 -f grip-gl-mai-v2
# python 14_run_validation_experiments.py -s grip-gl-mai   -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f grip-gl-mai-v2

# evaluate all regions with new model (grip-gl-mai-v3)
# python 14_run_validation_experiments.py -s wisconsin-lewis -u grip-gl-mai-v3  -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
# python 14_run_validation_experiments.py -s ontario-zhi     -u grip-gl-mai-v3  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
# python 14_run_validation_experiments.py -s grip-gl-mai     -u grip-gl-mai-v3  -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3
# python 14_run_validation_experiments.py -s conus-zhi       -u grip-gl-mai-v3  -p 1980-01-01:2018-12-31 -f conus-zhi-v1

# evaluate all models on a new region (camels-us-newman)
# module load mpi4py/3.1.3
# source /scratch/julemai/basin-fabric/env-cuda/bin/activate
# cd /scratch/julemai/basin-fabric/src
# python 14_run_validation_experiments.py -s camels-us-newman -u grip-gl-mai-v2  -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
# python 14_run_validation_experiments.py -s camels-us-newman -u grip-gl-mai-v3  -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
# python 14_run_validation_experiments.py -s camels-us-newman -u conus-zhi-v1    -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
# python 14_run_validation_experiments.py -s camels-us-newman -u conus-zhi-v2    -p 1980-01-01:2018-12-31 -f camels-us-newman-v1

# evaluate all regions with new model (camels-us-newman-v1)  LATER
# module load mpi4py/3.1.3
# source /scratch/julemai/basin-fabric/env-cuda/bin/activate
# cd /scratch/julemai/basin-fabric/src
# python 14_run_validation_experiments.py -s wisconsin-lewis  -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
# python 14_run_validation_experiments.py -s ontario-zhi      -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
# python 14_run_validation_experiments.py -s grip-gl-mai      -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3
# python 14_run_validation_experiments.py -s conus-zhi        -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f conus-zhi-v1
# python 14_run_validation_experiments.py -s camels-us-newman -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f camels-us-newman-v1

# evaluate all models on a new region (lake-erie-us-gaffney)
# module load mpi4py/3.1.3
# source /scratch/julemai/basin-fabric/env-cuda/bin/activate
# cd /scratch/julemai/basin-fabric/src
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1

# evaluate all models on a new region (north-america-mai)
# module load mpi4py/3.1.3
# source /scratch/julemai/basin-fabric/env-cuda/bin/activate
# cd /scratch/julemai/basin-fabric/src
# python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f north-america-mai-v1
# python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f north-america-mai-v1
# python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f north-america-mai-v1
# python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f north-america-mai-v1
# python 14_run_validation_experiments.py -s north-america-mai -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1

# evaluate all regions with new model (north-america-mai-v1)  LATER
# module load mpi4py/3.1.3
# source /scratch/julemai/basin-fabric/env-cuda/bin/activate
# cd /scratch/julemai/basin-fabric/src
# python 14_run_validation_experiments.py -s wisconsin-lewis      -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1
# python 14_run_validation_experiments.py -s ontario-zhi          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f ontario-zhi-v1
# python 14_run_validation_experiments.py -s grip-gl-mai          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3
# python 14_run_validation_experiments.py -s conus-zhi            -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f conus-zhi-v1
# python 14_run_validation_experiments.py -s camels-us-newman     -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f camels-us-newman-v1
# python 14_run_validation_experiments.py -s north-america-mai    -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1


do_setup    = False
do_evaluate = False
do_merge    = False
do_netcdf   = True     # might require increase of requested memory because of pkl read :(
                        # 16GB conus-zhi        - 513 basins - 39 years
                        # 50GB camels-us-newman - 671 basins - 39 years



"""

Runs basins specified in case study (-s) using the LSTM trained for (potentially)
another region (-u).


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
Written,  JM, Aug 2023 - initial script

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse

from   pathlib  import Path
import glob
import os
import shutil
import datetime as datetime
import subprocess
import xarray as xr
import pickle
import pandas as pd

case_study   = None
using_lstm   = None
period       = None
forcings     = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive streamflow for case study basins using trained LSTM specified.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai'].")
parser.add_argument('-u', '--using_lstm', action='store', default=using_lstm, dest='using_lstm',
                    help="Name of region the LSTM was trained for which will be used to derive predictions for basins of case study (-s). Can be the same as case_study. Then basins will just be evaluated, e.g., for a longer time period. The name provided needs to be the name of a folder in 'lstm/'.")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Period to retrieve data for. Format: YYYY-MM-DD:YYYY-MM-DD. ")
parser.add_argument('-f', '--forcings', action='store', default=forcings, dest='forcings',
                    help="Folder that contains frocing folder 'time_series'. Might require running 09_merge_forcings_and_observations first. For example, wisconsin-lewis-v1. Is a folder under 'lstm/'. ")

args         = parser.parse_args()
case_study   = args.case_study
using_lstm   = args.using_lstm
period       = args.period
forcings     = args.forcings

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai', 'camels-us-newman', 'north-america-mai']")

if (using_lstm is None):
    raise ValueError("Name of region with trained LSTM needs to be specified. For example, 'conus-zhi-v2'.")

if not(period is None):
    start = period.split(':')[0]
    start = datetime.datetime.strptime(start, '%Y-%m-%d').strftime("%d/%m/%Y")
    end   = period.split(':')[1]
    end   = datetime.datetime.strptime(end,   '%Y-%m-%d').strftime("%d/%m/%Y")
    period = {'start':start, 'end':end}
else:
    raise ValueError('Period needs to be specified. Format: YYYY-MM-DD:YYYY-MM-DD. ')

if (forcings is None):
    raise ValueError("Name of LSTM folder that contains 'time_series' is required. Might require running 09_merge_forcings_and_observations first.")

del parser, args


pyenv = str(Path(str(Path(__file__).parent)+'/../env-cuda/bin/activate'))

project_root = Path(str(Path(__file__).parent)+'/../regions/'+case_study+'/')
if not( project_root.exists() ):
    raise ValueError('Case study for {} not setup yet.'.format(case_study))
project_root = Path(str(Path(__file__).parent)+'/../regions/'+case_study+'/predictions/using_'+using_lstm+'/')

lstm_root = Path(str(Path(__file__).parent)+'/../lstm/'+using_lstm+'/runs/')
if not( lstm_root.exists() ):
    raise ValueError('LSTM seems to be not available for {}.'.format(using_lstm))


if do_setup:

    # ----------------------------
    # create folder under region for predictions
    # ----------------------------
    if not os.path.exists(project_root):
        os.makedirs(project_root)
    else:
        #raise ValueError('Predictions already exist. Please delete or save folder first:\n{}'.format(project_root))
        print('Overwritten folder')

    # ----------------------------
    # create local folder structure
    # ----------------------------
    folders = ['basins', 'attributes', 'runs', 'ensemble']
    for ff in folders:
        if not(os.path.exists(Path.joinpath(project_root,ff))):
            os.makedirs(Path.joinpath(project_root,ff))

    # ----------------------------
    # link forcings folder
    # ----------------------------
    src = Path(str(Path(__file__).parent)+'/../lstm/'+forcings+'/time_series')
    dst = Path.joinpath(project_root,'time_series')
    if not(os.path.exists(dst)):
        os.symlink(src,dst)

    # ----------------------------
    # create file containing all basins (based on where we have forcings)
    # ----------------------------
    filename = 'basins/basins.txt'
    dst = Path.joinpath(project_root,Path(filename))
    basin_file = str(dst)

    # just the basins where we have forcings for
    basins = [ '.'.join(gg.split('/')[-1].split('.')[0:-1]) for gg in glob.glob(str(Path.joinpath(project_root,'time_series'))+'/*.nc') ]

    cc = 0
    ff = open(dst, "w")
    for bb in basins:
        ff.write(bb+'\n')
        cc += 1
    ff.close()
    print('Number of basins that will be predicted: {}'.format(cc))

    # ----------------------------
    # link attributes folder
    # ----------------------------
    src = Path(str(Path(__file__).parent)+'/../regions/'+case_study+'/attributes/static_attributes.csv')
    dst = Path.joinpath(project_root,'attributes', 'static_attributes.csv')
    if not(os.path.exists(dst)):
        os.symlink(src,dst)

    src = Path(str(Path(__file__).parent)+'/../regions/'+case_study+'/attributes/climate_indices_rdrs-v2.1_north-america.csv')
    dst = Path.joinpath(project_root,'attributes', 'climate_indices.csv')
    if not(os.path.exists(dst)):
        os.symlink(src,dst)

    # ----------------------------
    # get folders of trained LSTM
    # ----------------------------
    folders_lstm = glob.glob( str(Path.joinpath(lstm_root,'*finalTraining-seed*')) )
    if len(folders_lstm) != 10:
        raise ValueError('LSTM does not seem to have 10 ensemble members; only {}.\nSee under: {}'.format(
            len(folders_lstm),Path.joinpath(lstm_root,'*finalTraining-seed*') ))

    # ----------------------------
    # create setting for ensemble
    # ----------------------------
    for folder_lstm in folders_lstm:

        src_folder = Path(folder_lstm)
        dst_folder = Path.joinpath(project_root,Path('runs'),Path(folder_lstm).name)

        # ----------------------------
        # create necessary folder structure
        # ----------------------------
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        if not os.path.exists(Path.joinpath(dst_folder,'train_data')):
            os.makedirs(Path.joinpath(dst_folder,'train_data'))
        if not os.path.exists(Path.joinpath(dst_folder,'../../basins')):
            os.makedirs(Path.joinpath(dst_folder,'../../basins'))

        # ----------------------------
        # copy yml
        # ----------------------------
        filename = 'config.yml'
        src = Path.joinpath(src_folder,Path(filename))
        dst = Path.joinpath(dst_folder,Path(filename))
        shutil.copy(src, dst)

        # ----------------------------
        # copy scaler
        # ----------------------------
        filename = 'train_data/train_data_scaler.yml'
        src = Path.joinpath(src_folder,Path(filename))
        dst = Path.joinpath(dst_folder,Path(filename))
        shutil.copy(src, dst)

        # ----------------------------
        # link last epoch
        # ----------------------------
        filename = 'model_epoch030.pt'
        src = Path.joinpath(src_folder,Path(filename))
        dst = Path.joinpath(dst_folder,Path(filename))
        shutil.copy(src, dst)

        # ----------------------------
        # adjust yml
        # ----------------------------
        filename = 'config.yml'
        filename = Path.joinpath(dst_folder,Path(filename))
        ff = open(filename, "r")
        lines = ff.readlines()
        ff.close()

        # a- get old data_dir
        for iline,line in enumerate(lines):
            if line.startswith('data_dir:'):
                old_data_dir = line.split(':')[1].strip()

        # b- replace old data_dir with new ones everywhere
        for iline,line in enumerate(lines):
            if old_data_dir in line:
                lines[iline] = line.replace(old_data_dir,str(project_root))

        # c- change test period to full period (TODO make those command line arguments)
        for iline,line in enumerate(lines):
            if line.startswith('test_end_date:'):
                lines[iline] = 'test_end_date: '+period['end']+' \n'
            if line.startswith('test_start_date:'):
                lines[iline] = 'test_start_date: '+period['start']+' \n'

        # d- change name of file containing basin names
        for iline,line in enumerate(lines):
            if line.startswith('test_basin_file:'):
                lines[iline] = 'test_basin_file: '+basin_file+' \n'
            if line.startswith('train_basin_file:'):
                lines[iline] = 'train_basin_file: '+basin_file+' \n'
            if line.startswith('validation_basin_file:'):
                lines[iline] = 'validation_basin_file: '+basin_file+' \n'

        # e- change number of basins
        for iline,line in enumerate(lines):
            if line.startswith('number_of_basins:'):
                lines[iline] = 'number_of_basins: '+str(len(basins))+' \n'


        # d- write to file
        ff = open(filename, "w")
        for iline,line in enumerate(lines):
            ff.write(line)
        ff.close()

else:
    if do_evaluate or do_merge:
        folders_lstm = glob.glob( str(Path.joinpath(Path(lstm_root),Path('*finalTraining-seed*'))) )
        if len(folders_lstm) != 10:
            raise ValueError('LSTM does not seem to have 10 ensemble members; only {}.\nSee under: {}'.format(
                len(folders_lstm),Path.joinpath(lstm_root,'*finalTraining-seed*') ))


if do_evaluate:

    # -------------------------------------
    # Evaluate trained model
    # - creates: <project_root>/runs/conus-zhi-finalTraining-seed5_2407_130608/test/model_epoch030/test_metrics.csv
    # - creates: <project_root>/runs/conus-zhi-finalTraining-seed5_2407_130608/test/model_epoch030/test_results.p
    # -------------------------------------
    for folder_lstm in folders_lstm:

        folder_to_evaluate = Path.joinpath(Path(project_root),Path('runs'),Path(folder_lstm).name)
        file_to_create     = Path.joinpath(folder_to_evaluate,Path('test/model_epoch030/test_results.p'))
        if not(os.path.exists(file_to_create)):
            print('do   evaluate '+folder_lstm)

            # nh-run evaluate --run-dir runs/grip-gl-finalTraining-seed1_XXXX_XXXXXX/
            cmd = 'nh-run evaluate --run-dir '+str(folder_to_evaluate)+'/'
            print(cmd)
            subprocess.run(cmd, shell=True)
        else:
            print('Folder exited already: {}'.format(file_to_create))


folder_to_merge     = Path.joinpath(Path(project_root),Path('ensemble'))
file_to_create      = Path.joinpath(folder_to_merge,Path('test_ensemble_results.p'))
if do_merge:

    # -------------------------------------
    # Merge ensembles (average their predictions)
    # - creates: <project_root>/ensemble/test_ensemble_metrics.csv
    # - creates: <project_root>/ensemble/test_ensemble_results.p
    # -------------------------------------

    list_folder_lstm = ' '.join([ str(Path.joinpath(Path(project_root),Path('runs'),Path(folder_lstm).name))+'/' for folder_lstm in folders_lstm ])

    if not(os.path.exists(file_to_create)):

        # nh-results-ensemble --run-dirs runs/grip-gl-finalTraining-seed* --output-dir final-training
        cmd = 'nh-results-ensemble --run-dirs '+list_folder_lstm+' --output-dir '+str(folder_to_merge)+'/'
        print(cmd)
        subprocess.run(cmd, shell=True)

        print('Wrote: {}'.format(file_to_create))
    else:
        print('File existed already: {}'.format(file_to_create))

# -------------------------------------
# Create NetCDF with all predictions
# -------------------------------------

netcdf_file = Path.joinpath(folder_to_merge,Path('test_ensemble_results.nc'))
if do_netcdf:

    if not(os.path.exists(netcdf_file)):
        results_file = pickle.load(open(file_to_create, 'rb'))

        static_attributes = pd.read_csv(Path.joinpath(project_root,'attributes', 'static_attributes.csv'), index_col=[0], dtype={'basin': 'str'})

        all_results = []
        #cc = 0
        for basin, basin_results in results_file.items():
            #cc += 1
            #print('Working on basin {} ({} of {})'.format(basin,cc,len(results_file.items())))
            
            xr_results = basin_results['1D']['xr']

            # clip values to >= 0
            xr_results['qobs_mm_per_day_sim'] = xr.where(xr_results['qobs_mm_per_day_sim'] < 0,
                                                         0, xr_results['qobs_mm_per_day_sim'])

            area = static_attributes.loc[basin, 'area_km2'] * 1000_000  # km2 -> m2
            xr_results = xr_results * area / (60 * 60 * 24 * 1000.0)  # mm/d -> m3/s
            xr_results = xr_results.rename({f'qobs_mm_per_day_{x}': f'qobs_m3_per_s_{x}'
                                            for x in ['obs', 'sim']})

            xr_results = xr_results.expand_dims('basin')
            xr_results['basin'] = [basin]
            all_results.append(xr_results)

        # # takes really long and uses HUGE amounts of RAM
        # all_results = xr.merge(all_results) 
        # # assumes that there are no conflicts between datasets (but that shouldnt be the case anyway)
        all_results = xr.combine_nested(all_results,concat_dim='basin')
        
        all_results.to_netcdf(netcdf_file)

        print('Wrote: {}'.format(netcdf_file))
    else:
        print('File existed already: {}'.format(netcdf_file))
