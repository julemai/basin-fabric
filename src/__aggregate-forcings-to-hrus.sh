#!/bin/bash

# Copyright 2016-2022 Juliane Mai - contact[at]juliane-mai[dot]com
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
#
# ./04_aggregate-forcings-to-hrus.sh -b 01010400202 -o lp -f RDRS_v2.1   # not really tested in this example but that was what it was before chnaging to ERA5
# ./04_aggregate-forcings-to-hrus.sh -b 01010400202 -o ds -f RDRS_v2.1   # not really tested in this example but that was what it was before chnaging to ERA5
# ./04_aggregate-forcings-to-hrus.sh -b 01010400202 -o lp -f ERA5_Land
# ./04_aggregate-forcings-to-hrus.sh -b 01010400202 -o ds -f ERA5_Land

set -ex

prog=$0
pprog=$(basename ${prog})
dprog=$(dirname ${prog})
isdir=${PWD}
pid=$$

function usage () {
    printf "${pprog}                                                                \n"
    printf "Aggregate forcings to HRUs                                              \n"
    printf "                                                                        \n"
    printf "Input                                                                   \n"
    printf "    None                                                                \n"
    printf "                                                                        \n"
    printf "Options                                                                 \n"
    printf "    -h               Prints this help screen.                           \n"
    printf "    -b               Basin ID, e.g., 01010400202                        \n"
    printf "                     Default: None                                      \n"
    printf "    -f               File type. Either ERA5_Land or RDRS_v2.1           \n"
    printf "                     Default: None                                      \n"
    printf "    -o               Option. Either lp or ds                            \n"
    printf "                     Default: None                                      \n"
    printf "                                                                        \n"
    printf "Example                                                                 \n"
    printf "    ${pprog} -b 01010400202 -f ERA5_Land                                \n"
}

basin="None"
option="None"
filetype="None"
while getopts "hb:f:o:" Option ; do
    case ${Option} in
        h) usage 1>&2; exit 0;;
        b) basin="${OPTARG}";;
	o) option="${OPTARG}";;
	f) filetype="${OPTARG}";;
        *) printf "Error ${pprog}: unimplemented option.\n\n";  usage 1>&2; exit 1;;
    esac
done
shift $((${OPTIND} - 1))

# Check if basin is given
if [[ ${basin} == 'None' ]] ; then
    printf "Error ${pprog}: Basin (-b) must be given.\n"
    exit 1
fi

# Check if discretization option is specified
if [[ ${option} == 'None' ]] ; then
    printf "Error ${pprog}: Discretization option (-o) must be given. Either 'lp' (lumped) or 'ds' (distributed).\n"
    exit 1
fi
case ${option} in
    'lp') ok='True' ;;
    'ds') ok='True' ;;
    *) printf "Error ${pprog}: Option (-o) needs to be either 'lp' or 'ds'.\n\n";  usage 1>&2; exit 1;;
esac

# Check if filetype option is specified
if [[ ${filetype} == 'None' ]] ; then
    printf "Error ${pprog}: Filetype option (-f) must be given. Either 'ERA5_Land' or 'RDRS_v2.1'.\n"
    exit 1
fi
case ${filetype} in
    'ERA5_Land') ok='True' ;;
    'RDRS_v2.1') ok='True' ;;
    *) printf "Error ${pprog}: Filetype (-f) must be either 'ERA5_Land' or 'RDRS_v2.1'.\n\n";  usage 1>&2; exit 1;;
esac



# module purge
# module load StdEnv/2020 netcdf gcc/9.3.0 gdal/3.0.4
# module load mpi4py/3.1.3 proj/9.0.1
# module load python/3.8.10 geos/3.8.1
# module load nco/5.0.6

# source /project/6070465/julemai/blended-model-na/env-3.8/bin/activate

if [[ ${filetype} == 'RDRS_v2.1' ]] ; then
    vars="RDRS_v2.1_A_PR0_SFC RDRS_v2.1_P_PR0_SFC RDRS_v2.1_P_TT_1.5m"
    weightsfile="${isdir}/../data_in/data_obs/${basin}/${basin}_gridweights_${filetype}_${option}.txt"
    dimnames="rlon rlat"

else
    if [[ ${filetype} == 'ERA5_Land' ]] ; then
	vars='ro'
	weightsfile="${isdir}/shapefiles/${basin}/${basin}_gridweights_${filetype}_${option}.txt"
	dimnames="rlon rlat"

    else
	echo "Filetype (-f) must be either 'ERA5_Land' or 'RDRS_v2.1'."
    fi
fi

for var in ${vars} ; do

    echo "Aggregating files for variable ${var} ..."

    if [[ ${filetype} == 'RDRS_v2.1' ]] ; then
	netcdffiles=$( \ls ${isdir}/gridded_data/rdrs_v2.1_${var}.nc )
    else
	if [[ ${filetype} == 'ERA5_Land' ]] ; then
	    netcdffiles=$( \ls ${isdir}/gridded_data/grip-gl_era5-land_${var}.nc )
	fi
    fi


    zipfile="${isdir}/shapefiles/${basin}/${basin}_agg_${filetype}_${option}_${var}.zip"
    for netcdffile in ${netcdffiles}; do

	# find date in filename
	aggfile="${isdir}/shapefiles/${basin}/${basin}_agg_${filetype}_${option}_${var}.nc"
	donefile="${isdir}/shapefiles/${basin}/${basin}_agg_${filetype}_${option}_${var}.done"

	if [ ! -e ${zipfile} ] ; then
	    if [ ! -e ${donefile} ] ; then

		# corrupted aggfile might exist --> clean up
		if [ -e ${aggfile} ] ; then rm ${aggfile} ; fi

		# aggregate
		ravenpy aggregate-forcings-to-hrus --output-nc-file ${aggfile} --var-to-aggregate ${var} --dim-names ${dimnames} ${netcdffile} ${weightsfile}

		# make time UNLIMITED
		ncks --mk_rec_dmn time ${aggfile} ${aggfile}.new
		mv ${aggfile}.new ${aggfile}

		# create donefile
		touch ${donefile}
	    fi
	fi

    done

    # # merge to one file
    # echo "Merging aggregated files for variable ${var} ..."

    # files="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_*_${var}.nc"
    # mergefile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_hourly_${var}.nc"
    # if [ ! -e ${mergefile} ] ; then
    # 	ncrcat -h ${files} ${mergefile}
    # fi

    # # zip all annual files to reduce number of files created
    # echo "Zipping annual files for variable ${var} ..."
    # if [ ! -e ${zipfile} ] ; then

    # 	cd "${isdir}/../data_in/data_obs/${basin}"
    # 	zipfile="${basin}_agg_${option}_${var}.zip"
    # 	zip ${zipfile} ${basin}_agg_${option}_[1-2]*_${var}.nc ${basin}_agg_${option}_[1-2]*_${var}.done
    # 	rm ${basin}_agg_${option}_[1-2]*_${var}.nc
    # 	rm ${basin}_agg_${option}_[1-2]*_${var}.done
    # 	cd -

    # fi

    # # shift time from UTC to local
    # localfile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_hourly_local_${var}.nc"
    # #shift=$( grep "^${basin};" "${isdir}/../data_in/basins_3896_time_offset.dat" | cut -d ';' -f 2 )
    # shift=$( grep "^${basin};" "${isdir}/../data_in/basins_2577_time_offset.dat" | cut -d ';' -f 2 )
    # if [ ! -e ${localfile} ] ; then
    # 	shift_str="time+=${shift}"    # 'time+=-5.0' works; does not need to be 'time-=5.0'
    # 	ncap2 -s ${shift_str} ${mergefile} ${localfile}
    # fi

    # # # convert from hourly to daily file
    # # ncra --mro -d time,,,24,24        hourly.nc daily_min.nc
    # # ncra --mro -d time,,,24,24 -y min hourly.nc daily_min.nc
    # # ncra --mro -d time,,,24,24 -y max hourly.nc daily_max.nc
    # # ncra --mro -d time,,,24,24 -y ttl hourly.nc daily_sum.nc
    # skip_timesteps=$(( 24-(13+${shift%.*})  ))   # number of timesteps that are for Jan 1, 1980 (incomplete day) --> skip
    # if [[ ${var} == 'RDRS_v2.1_A_PR0_SFC' || ${var} == 'RDRS_v2.1_P_PR0_SFC' ]] ; then
    # 	# sum 24 time steps
    # 	dailyfile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_daily_local_${var}_sum.nc"
    # 	tmpfile="${isdir}/../data_in/data_obs/${basin}/tmp.nc"
    # 	if [ ! -e ${dailyfile} ] ; then
    # 	    ncra --mro -d time,${skip_timesteps},,24,24 -y ttl ${localfile} ${dailyfile}
    # 	    # since time is also averaged all timesteps will be at 12:00 --> move to 00:00
    # 	    ncap2 -s "time-=12" ${dailyfile} ${tmpfile}
    # 	    mv ${tmpfile} ${dailyfile}
    # 	fi
    # else
    # 	if [[ ${var} == 'RDRS_v2.1_P_TT_1.5m' ]] ; then
    # 	    # average 24 time steps
    # 	    dailyfile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_daily_local_${var}_avg.nc"
    # 	    tmpfile="${isdir}/../data_in/data_obs/${basin}/tmp.nc"
    # 	    if [ ! -e ${dailyfile} ] ; then
    # 		ncra --mro -d time,${skip_timesteps},,24,24        ${localfile} ${dailyfile}
    # 		# since time is also averaged all timesteps will be at 12:00 --> move to 00:00
    # 		ncap2 -s "time-=12" ${dailyfile} ${tmpfile}
    # 		mv ${tmpfile} ${dailyfile}
    # 	    fi

    # 	    # minimum 24 time steps
    # 	    dailyfile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_daily_local_${var}_min.nc"
    # 	    tmpfile="${isdir}/../data_in/data_obs/${basin}/tmp.nc"
    # 	    if [ ! -e ${dailyfile} ] ; then
    # 		ncra --mro -d time,${skip_timesteps},,24,24 -y min ${localfile} ${dailyfile}
    # 		# since time is also minimized all timesteps will be at 11:00 --> move to 00:00
    # 		ncap2 -s "time-=11" ${dailyfile} ${tmpfile}
    # 		mv ${tmpfile} ${dailyfile}
    # 	    fi

    # 	    # maximum 24 time steps
    # 	    dailyfile="${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_daily_local_${var}_max.nc"
    # 	    tmpfile="${isdir}/../data_in/data_obs/${basin}/tmp.nc"
    # 	    if [ ! -e ${dailyfile} ] ; then
    # 		ncra --mro -d time,${skip_timesteps},,24,24 -y max ${localfile} ${dailyfile}
    # 		# since time is also maximized all timesteps will be at 11:00 --> move to 00:00
    # 		ncap2 -s "time-=11" ${dailyfile} ${tmpfile}
    # 		mv ${tmpfile} ${dailyfile}
    # 	    fi
    # 	else
    # 	    echo "No averaging implemented for variable = ${var}"
    # 	fi
    # fi

    # cleanup
    # - remove created RVT files with new weights
    #rm "${isdir}/../data_in/data_obs/${basin}/${basin}_gridweights_RDRS_v2.1_${option}_aggregated.rvt"
    # - remove merged file in UTC time
    #rm ${mergefile}
    # - remove annual files (these take really long to create --> make sure you really want to remove them)
    #rm "${isdir}/../data_in/data_obs/${basin}/${basin}_agg_${option}_[0-9]*_${var}.nc"

done

touch ${isdir}/shapefiles/${basin}/${basin}_${filetype}_${option}.done
