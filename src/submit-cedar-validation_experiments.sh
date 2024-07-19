#!/bin/bash

# submit with:
#       cd /project/6067703/julemai/src
#       sbatch submit-cedar-validation_experiments.sh

#SBATCH --account=def-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=END,FAIL                       # email send only in case of failure

#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1

#SBATCH --job-name=lstm-eval                       # name of job in queque

## -----------------------------------------------------------------------------------------------
## step 2-3 (evaluate + merge)
##SBATCH --time=2-00:00:00                          # time (DD-HH:MM:SS);
##SBATCH --mem=16G                                  # memory; default unit is megabytes
## -----------------------------------------------------------------------------------------------
## step 4 (netcdf)
#SBATCH --time=0-06:00:00                          # time (DD-HH:MM:SS);
#SBATCH --mem=200G                                  # memory; default unit is megabytes
## -----------------------------------------------------------------------------------------------

# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# Load some modules
module load StdEnv/2023 gcc/12.3 netcdf/4.9.2 gdal/3.7.2 mpi4py/3.1.4 proj/9.2.0 geos/3.12.0 nco/5.1.7 python/3.11.5

# Load Python env
source /project/6067703/julemai/env-3.11-cuda/bin/activate

# Do evaluation
cd /project/6067703/julemai/src

# # evaluate all models on a new region (north-america-mai)                                                                                      # --------- step 2-3 ---------------
python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071584   
python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071556
# python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071575
python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071610
python 14_run_validation_experiments.py -s north-america-mai -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071617

# # evaluate all regions with new model (north-america-mai-v1)                                                                                   # --------- step 2-3 ---------------
# python 14_run_validation_experiments.py -s wisconsin-lewis      -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1         #   (47) 5min/seed  1.0h  DONE interactively
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1    #   (78) 9min/seed  2.0h  DONE interactively
# python 14_run_validation_experiments.py -s ontario-zhi          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f ontario-zhi-v1             #  (361) ??/seed   10.0h  1.0GB  37071442
# python 14_run_validation_experiments.py -s grip-gl-mai          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3             #  (212) ??/seed    2.5h  1.0GB  37071384
# python 14_run_validation_experiments.py -s conus-zhi            -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f conus-zhi-v1               #  (513) ??/seed   12.0h  1.5GB  37071357
# python 14_run_validation_experiments.py -s camels-us-newman     -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f camels-us-newman-v1        #  (671) ??/seed    8.0h  1.5GB  37071314
# python 14_run_validation_experiments.py -s north-america-mai    -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1       # (2575) 3h/seed      3d  ???   37071252


