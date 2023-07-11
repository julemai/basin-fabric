#!/bin/bash

# submit with:
#       sbatch submit-to-graham-rio-merge.sh

#SBATCH --account=rpp-julemai                      # your group rpp-kshook
#SBATCH --mem-per-cpu=20GB                         # memory; default unit is megabytes
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure
#SBATCH --time=0-01:00:00                          # time (DD-HH:MM:SS);
#SBATCH --job-name=merge-files                     # name of job in queque


module load StdEnv/2020
module load netcdf/4.7.4
module load gcc/9.3.0
module load gdal/3.5.1
module load mpi4py/3.1.3
module load proj/9.0.1
module load geos/3.10.2
module load nco/5.0.6
module load python/3.10.2

# load Python environment
source /home/julemai/env-3.10/bin/activate

# change path where files are
cd /scratch/julemai/basin-fabric/data/dem

# merge files
rio merge *_dem_3s_zip_bil/*/*.bil na_ca_dem_3s.tif


# JOBID
# 9279639   --> merge dem bil files
