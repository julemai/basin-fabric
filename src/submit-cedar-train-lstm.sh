#!/bin/bash

# submit with:
#       cd /scratch/julemai/basin-fabric/src
#       sbatch submit-cedar-train-lstm.sh

#SBATCH --account=def-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure

#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --array=1-10

#SBATCH --job-name=lstm-grip                       # name of job in queque
#SBATCH --time=0-04:00:00                          # time (DD-HH:MM:SS);
#SBATCH --mem=3G                                   # memory; default unit is megabytes


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

# Do training
cd /scratch/julemai/basin-fabric/lstm/grip-gl/                                # <<<<<<<<<<<<<<<<
nh-run train --config-file final-training/seed${SLURM_ARRAY_TASK_ID}.yml



# ------------------
# grip-gl
# ------------------
# JOBID
# 7606862   --> all basins                        ;  3GB ; 4h   ; 10 tasks (each 1 seed)
