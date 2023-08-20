#!/bin/bash

# submit with:
#       sbatch submit-cedar-train-lstm.sh

#SBATCH --account=def-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure

#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --array=1  #1,3,4,5,7,9

#SBATCH --job-name=lstm-conus-zhi-v2               # name of job in queque
#SBATCH --time=0-23:00:00                          # time (DD-HH:MM:SS);                 # <<<<<<<<<<<<<<<<
#SBATCH --mem=12G                                   # memory; default unit is megabytes   # <<<<<<<<<<<<<<<<


# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# Load some modules
module load StdEnv/2020
module load netcdf/4.7.4
module load gcc/9.3.0
module load gdal/3.5.1
module load mpi4py/3.1.3
module load proj/9.0.1
module load geos/3.10.2
module load nco/5.0.6
module load python/3.10.2

# Load Python env
source /scratch/julemai/basin-fabric/env-cuda/bin/activate

# experiment tag
tag='conus-zhi-v2'      # <<<<<<<<<<<<<<<<

# Do training
# - creates: runs/${tag}-finalTraining-seedX_XXXX_XXXXXX/
cd /scratch/julemai/basin-fabric/lstm/${tag}/
nh-run train --config-file final-training/seed${SLURM_ARRAY_TASK_ID}.yml

# Do evaluation
# - creates: runs/${tag}-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_metrics.csv
# - creates: runs/${tag}-finalTraining-seedX_XXXX_XXXXXX/test/model_epoch030/test_results.p
folder=$( \ls -d runs/${tag}-finalTraining-seed${SLURM_ARRAY_TASK_ID}_* )   # runs/grip-gl-finalTraining-seed10_XXXX_XXXXXX/
nh-run evaluate --run-dir ${folder}/

# ------------------
# ${tag}
# ------------------
# JOBID
# 8361305   --> all basins                        ;  9GB ; 23h   ; 10 tasks (each 1 seed)
# 8395248   --> all basins                        ; 12GB ; 23h   ; 5 tasks that were out of memory
# 10048709  --> all basins                        ; 12GB ; 23h   ; 1 task  that was cancelled
