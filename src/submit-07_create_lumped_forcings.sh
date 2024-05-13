#!/bin/bash


# License
# -------
# This file is part of the Basin Fabric which contains scripts to
# process data for basins, deriving attributes, processing forcings,
# and setting up and training data-driven models.

# The Basin Fabric code is free software: you can redistribute it
# and/or modify it under the terms of the MIT License.

# The Basin Fabric code library is distributed in the hope that it will
# be useful,but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
# License for more details.

# You should have received a copy of the MIT License along with the
# Basin Fabric code. If not, see
# <https://github.com/julemai/basin-fabric/blob/main/LICENSE>.

# Copyright 2023-2024 Juliane Mai - juliane.mai@uwaterloo.ca



# submit with:
#       sbatch submit-07_create_lumped_forcings.sh

#SBATCH --account=rpp-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=FAIL                           # email send only in case of failure

##SBATCH --job-name=agg-conus                      # name of job in queque
##SBATCH --time=3-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-257

##SBATCH --job-name=agg-wi                         # name of job in queque
##SBATCH --time=1-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-47

##SBATCH --job-name=agg-grip                       # name of job in queque
##SBATCH --time=1-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-212

##SBATCH --job-name=agg-ontario                    # name of job in queque
##SBATCH --time=1-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-361

##SBATCH --job-name=agg-camels                     # name of job in queque
##SBATCH --time=0-01:00:00    # 3-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-224

##SBATCH --job-name=agg-erie-us                    # name of job in queque
##SBATCH --time=0-01:00:00   # 3-00:00:00                         # time (DD-HH:MM:SS);
##SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
##SBATCH --array=1-78

#SBATCH --job-name=agg-na                          # name of job in queque
#SBATCH --time=3-00:00:00                          # time (DD-HH:MM:SS);
#SBATCH --mem-per-cpu=1G                           # memory; default unit is megabytes
#SBATCH --array=1-515




# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# 1 basin  --> runtime: 16h for RDRS-v2.1 over North America   -->  --time=3-00:00:00  (2 basin/task)
# 1 basin  --> runtime: 16h for RDRS-v2.1 over North America   -->  --time=1-00:00:00  (1 basin/task)

# load modules
# module load StdEnv/2020
# module load netcdf/4.7.4
# module load gcc/9.3.0
# module load gdal/3.5.1
# module load mpi4py/3.1.3
# module load proj/9.0.1
# module load geos/3.10.2
# module load nco/5.0.6
# module load python/3.10.2

# load modules
module load StdEnv/2023 gcc/12.3 netcdf/4.9.2 gdal/3.7.2 mpi4py/3.1.4 proj/9.2.0 geos/3.12.0 nco/5.1.7 python/3.11.5

# load pyenv
# source /home/julemai/env-3.10/bin/activate
source /scratch/julemai/basin-fabric/env-3.11/bin/activate

# change to right dir
cd /scratch/julemai/basin-fabric/src/


# ----------------------------------------------------------------------------------------

# # set number of tasks (make sure it is consistent with above)
# ntasks=257                          # <<<<<<<<<<<<<<<<
# region="conus-zhi"                  # <<<<<<<<<<<<<<<<
# region_tag_python="conus-zhi"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# # set number of tasks (make sure it is consistent with above)
# ntasks=47                           # <<<<<<<<<<<<<<<<
# region="wisconsin-lewis"            # <<<<<<<<<<<<<<<<
# region_tag_python="wisconsin-lewis"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# # set number of tasks (make sure it is consistent with above)
# ntasks=212                            # <<<<<<<<<<<<<<<<
# region="grip-gl-mai"                  # <<<<<<<<<<<<<<<<
# region_tag_python="grip-gl-mai"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# # set number of tasks (make sure it is consistent with above)
# ntasks=361                            # <<<<<<<<<<<<<<<<
# region="ontario-zhi"                  # <<<<<<<<<<<<<<<<
# region_tag_python="ontario-zhi"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# # set number of tasks (make sure it is consistent with above)
# ntasks=224                                 # <<<<<<<<<<<<<<<<
# region="camels-us-newman"                  # <<<<<<<<<<<<<<<<
# region_tag_python="camels-us-newman"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# # set number of tasks (make sure it is consistent with above)
# ntasks=78                                 # <<<<<<<<<<<<<<<<
# region="lake-erie-us-gaffney"                  # <<<<<<<<<<<<<<<<
# region_tag_python="lake-erie-us-gaffney"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"

# set number of tasks (make sure it is consistent with above)
ntasks=515                                  # <<<<<<<<<<<<<<<<
region="north-america-mai"                  # <<<<<<<<<<<<<<<<
region_tag_python="north-america-mai"
forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"



# ----------------------------------------------------------------------------------------

# get basins to aggregate
nbasins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | wc -l )
# nbasins=$( cat /scratch/julemai/basin-fabric/regions/camels-us-newman/basins_missing.dat | wc -l )

#ibasins=$(( ${nbasins} / ${ntasks} + 1 ))   # number of basins per array-task  (if division with remainder != 0)
ibasins=$(( ${nbasins} / ${ntasks} ))       # number of basins per array-task  (if division with remainder == 0)
start_idx=$(( (${SLURM_ARRAY_TASK_ID} - 1)*${ibasins} + 1 ))
end_idx=$((   (${SLURM_ARRAY_TASK_ID}    )*${ibasins}     ))

basins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | head -${end_idx} | tail -${ibasins} | rev | cut -d '/' -f 1 | rev )
#basins=$( cat "/scratch/julemai/basin-fabric/regions/camels-us-newman/basins_missing.dat" | head -${end_idx} | tail -${ibasins} )

for bb in ${basins} ; do

    # # check if and old file needs to be deleted
    # if [ ! -e /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_lp.nc ] ; then
    # 	last=$( \ls -latrh /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_*.nc_lp.nc | tail -1 | rev | cut -d ' ' -f 1 | rev )
    # 	rm ${last}
    # fi

    echo "Aggregate forcings for basin ${bb}"

    python 07_create_lumped_forcings.py -s ${region_tag_python} -b ${bb} -f ${forcings} -y graham
    touch /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}.done

done



# # remove last NC file created

# region='ontario-zhi'
# region='grip-gl-mai'
# region='camels-us-newman'
# region='lake-erie-us-gaffney'

# basins=$( \ls -d /scratch/julemai/basin-fabric/regions/${region}/shapefiles/* | rev | cut -d '/' -f 1 | rev )

# for bb in $basins ; do if [ ! -e /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_lp.nc ] ; then last=$( \ls -latrh /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_*.nc_lp.nc | tail -1 ) ; echo $bb ${last} ; fi ; done

# miss_file="/scratch/julemai/basin-fabric/regions/${region}/basins_missing.dat"
# for bb in $basins ; do if [ ! -e /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_lp.nc ] ; then last=$( \ls -latrh /scratch/julemai/basin-fabric/regions/${region}/forcings/${bb}/${bb}_agg_rdrs-v2.1_north-america_*.nc_lp.nc | tail -1 | rev | cut -d ' ' -f 1 | rev ) ; echo ${bb} > ${miss_file} ; rm ${last} ; fi ; done


# ------------------
# region_tag_python="conus-zhi"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
# ------------------
# JOBID
# 9383171   --> all basins                        ;  1GB ; 72h   ; 257 tasks (each 2 basins)

# ------------------
# region_tag_python="wisconsin-lewis"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
# ------------------
# JOBID
# 9383028   --> all basins                        ;  1GB ; 24h   ; 47 tasks (each 1 basin)


# ------------------
# region_tag_python="grip-gl-mai"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
# ------------------
# JOBID
# 9523378   --> all basins                        ;  1GB ; 24h   ; 212 tasks (each 1 basin)
# 9555769   --> all basins (hiccup graham)        ;  1GB ; 24h   ; 212 tasks (each 1 basin)


# ------------------
# region_tag_python="ontario-zhi"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
# ------------------
# JOBID
# 9523633   --> all basins                        ;  1GB ; 24h   ; 361 tasks (each 1 basin)
# 9555757   --> all basins (hiccup graham)        ;  1GB ; 24h   ; 361 tasks (each 1 basin)


# ------------------
# region_tag_python="camels-us-newman"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
#
# ------------------
# check completeness CAMELS-US forcings  (should be 671)
# ls /scratch/julemai/basin-fabric/regions/camels-us-newman/forcings/*/*.done | wc -l
# ls /scratch/julemai/basin-fabric/regions/camels-us-newman/forcings/*/*_agg_rdrs-v2.1_north-america_lp.nc | wc -l
# ------------------
# JOBID
# 10190113   --> all basins                        ;  1GB ; 24h   ; 224 tasks (each 3 basin)
# 10306759   --> all basins missing                ;  1GB ; 24h   ;  14 tasks (each 1 basin)
# 10346548   --> all basins missing                ;  1GB ; 24h   ;  14 tasks (each 1 basin)
# 10644434   --> one file (UU 2017) was missing    ;  1GB ;  1h   ; 78 tasks (each 1 basin)



# ------------------
# region_tag_python="lake-erie-us-gaffney"
# forcings="/scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/"
#
# ------------------
# check completeness Lake Erie US forcings  (should be 78)
# ls /scratch/julemai/basin-fabric/regions/lake-erie-us-gaffney/forcings/*/*.done | wc -l
# ls /scratch/julemai/basin-fabric/regions/lake-erie-us-gaffney/forcings/*/*_agg_rdrs-v2.1_north-america_lp.nc | wc -l
# ------------------
# JOBID
# 10574850   --> all basins                        ;  1GB ; 24h   ; 78 tasks (each 1 basin)
# 10609072   --> all basins missing                ;  1GB ; 48h   ; 78 tasks (each 1 basin)
# 10644275   --> one file (UU 2017) was missing    ;  1GB ;  1h   ; 78 tasks (each 1 basin)



# ls /scratch/julemai/basin-fabric/regions/grip-gl-mai/forcings/*/*_agg_rdrs-v2.1_north-america_lp.nc | rev | cut -d '/' -f 2 | rev | sort > merge_exists.dat
# ls /scratch/julemai/basin-fabric/regions/grip-gl-mai/forcings/*/*.done | rev | cut -d '/' -f 2 | rev | sort > done_exists.dat

# ls /scratch/julemai/basin-fabric/regions/ontario-zhi/forcings/*/*_agg_rdrs-v2.1_north-america_lp.nc | rev | cut -d '/' -f 2 | rev | sort > merge_exists.dat
# ls /scratch/julemai/basin-fabric/regions/ontario-zhi/forcings/*/*.done | rev | cut -d '/' -f 2 | rev | sort > done_exists.dat

# missing=$( comm -23 done_exists.dat merge_exists.dat )
# echo ${missing}

# 02HL008 02LC029 04040500

# for bb in ${missing} ; do python 07_create_lumped_forcings.py -s ${region_tag_python} -b ${bb} -f ${forcings} -y graham ; done

# --> delete corruped files manually
# /scratch/julemai/basin-fabric/regions/grip-gl-mai/forcings/02HL008/02HL008_agg_rdrs-v2.1_north-america_1989_RDRS_v2.1_A_PR0_SFC.nc_lp.nc
# /scratch/julemai/basin-fabric/regions/grip-gl-mai/forcings/02LC029/02LC029_agg_rdrs-v2.1_north-america_1987_RDRS_v2.1_P_PR0_SFC.nc_lp.nc
# /scratch/julemai/basin-fabric/regions/grip-gl-mai/forcings/04040500/04040500_agg_rdrs-v2.1_north-america_1985_RDRS_v2.1_P_UU_10m.nc_lp.nc

# for bb in ${missing} ; do python 07_create_lumped_forcings.py -s ${region_tag_python} -b ${bb} -f ${forcings} -y graham ; done
