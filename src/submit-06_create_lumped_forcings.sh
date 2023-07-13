#!/bin/bash

# submit with:
#       sbatch submit-06_create_lumped_forcings.sh

#SBATCH --account=rpp-julemai                      # rpp-julemai                      # your group
#SBATCH --mem-per-cpu=1G                           # memory; default unit is megabytes
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure
#SBATCH --time=3-00:00:00                          # time (DD-HH:MM:SS);
#SBATCH --job-name=aggregate                       # name of job in queque
#SBATCH --array=1-257


# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# 1 basin  --> runtime: 16h for RDRS-v2.1 over North America

# load modules
module load StdEnv/2020
module load netcdf/4.7.4
module load gcc/9.3.0
module load gdal/3.5.1
module load mpi4py/3.1.3
module load proj/9.0.1
module load geos/3.10.2
module load nco/5.0.6
module load python/3.10.2

# load pyenv
source /home/julemai/env-3.10/bin/activate

# change to right dir
cd /scratch/julemai/basin-fabric/src/


# set number of tasks (make sure it is consistent with above)
ntasks=257                          # <<<<<<<<<<<<<<<<
region="North_America_watersheds"   # <<<<<<<<<<<<<<<<
region_tag_python="North-America"
forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# get basins to aggregate
basins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | rev | cut -d '/' -f 1 | rev )
nbasins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | wc -l )

ibasins=$(( ${nbasins} / ${ntasks} + 1 ))   # number of basins per array-task  (if division with remainder != 0)
#ibasins=$(( ${nbasins} / ${ntasks} ))       # number of basins per array-task  (if division with remainder == 0)
start_idx=$(( (${SLURM_ARRAY_TASK_ID} - 1)*${ibasins} + 1 ))
end_idx=$((   (${SLURM_ARRAY_TASK_ID}    )*${ibasins}     ))

basins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | head -${end_idx} | tail -${ibasins} | rev | cut -d '/' -f 1 | rev )


for bb in ${basins} ; do

    echo "Aggregate forcings for basin ${bb}"

    python 06_create_lumped_forcings.py -s ${region_tag_python} -b ${bb} -f ${forcings} -y graham

done




# ------------------
# region_tag_python="North-America"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
# ------------------
# JOBID
# 9352971   --> all basins                        ;  1GB ; 72h   ; 257 tasks (each 2 basins)

# ------------------
# region_tag_python=""
# forcings=""
# ------------------
# JOBID
