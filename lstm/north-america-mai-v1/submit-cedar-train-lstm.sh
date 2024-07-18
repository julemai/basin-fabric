#!/bin/bash

# submit with:
#       sbatch submit-cedar-train-lstm.sh

#SBATCH --account=def-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure

#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --array=1-10

#SBATCH --job-name=lstm-na                         # name of job in queque
#SBATCH --time=5-00:00:00                          # time (DD-HH:MM:SS);                 # <<<<<<<<<<<<<<<<
#SBATCH --mem=62G                                  # memory; default unit is megabytes   # <<<<<<<<<<<<<<<<


# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# Load some modules
# module load StdEnv/2020
# module load netcdf/4.7.4
# module load gcc/9.3.0
# module load gdal/3.5.1
# module load mpi4py/3.1.3
# module load proj/9.0.1
# module load geos/3.10.2
# module load nco/5.0.6
# module load python/3.10.2

# Load some modules
module load StdEnv/2023 gcc/12.3 netcdf/4.9.2 gdal/3.7.2 mpi4py/3.1.4 proj/9.2.0 geos/3.12.0 nco/5.1.7 python/3.11.5

# Load Python env
source /home/julemai/projects/def-julemai/julemai/env-3.11-cuda/bin/activate

# Do training
#cd /home/julemai/projects/def-julemai/julemai/lstm/north-america-mai-v1/ # <<<<<<<<<<<<<<<<
#nh-run train --config-file final-training/seed${SLURM_ARRAY_TASK_ID}.yml

# Continue training
cd /home/julemai/projects/def-julemai/julemai/lstm/north-america-mai-v1/ # <<<<<<<<<<<<<<<<
nh-run continue_training --run-dir runs/north-america-mai-v1-finalTraining-seed${SLURM_ARRAY_TASK_ID}_1206_075810/

# ------------------
# north-america-mai-v1
# ------------------
# JOBID
# 33841822  --> all basins ; initial training (aborted 9/10 tasks due to time)  ;  62GB ; 5 days   ; 10 tasks (each 1 seed)
# 34351168  --> all basins ; restart                                            ;  62GB ; 5 days   ; 10 tasks (each 1 seed)
