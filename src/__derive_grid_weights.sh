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
# ./03_derive_grid_weights.sh -b 01010400202 -o lp -f RDRS_v2.1
# ./03_derive_grid_weights.sh -b 01010400202 -o ds -f RDRS_v2.1
# ./03_derive_grid_weights.sh -b 01010400202 -o lp -f ERA5_Land
# ./03_derive_grid_weights.sh -b 01010400202 -o ds -f ERA5_Land

# --> runtime = 5min


set -ex

prog=$0
pprog=$(basename ${prog})
dprog=$(dirname ${prog})
isdir=${PWD}
pid=$$

basin="None"
option="None"
filetype="None"
while getopts "hb:o:f:" Option ; do
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

# source /project/6070465/julemai/blended-model-na/env-3.8/bin/activate

if [[ ${filetype} == 'RDRS_v2.1' ]] ; then
    infile="${isdir}/gridded_data/1980010112_RDRS_v2.1_A_PR0_SFC.nc"     #"/scratch/julemai/test/1980010112_RDRS_v2.1_A_PR0_SFC.nc"
    dimname="rlon,rlat"
    varname="lon,lat"
else
    if [[ ${filetype} == 'ERA5_Land' ]] ; then
	infile="${isdir}/gridded_data/grip-gl_era5-land_ro.nc"
	dimname="rlon,rlat"
	varname="lon,lat"
    else
	echo "Filetype (-f) must be either 'ERA5_Land' or 'RDRS_v2.1'."
    fi
fi

outfile="${isdir}/shapefiles/${basin}/${basin}_gridweights_${filetype}_${option}.txt"
donefile=$( echo ${outfile} | rev | cut -d '.' -f 2- | rev )".done"

if [[ ${option} == 'lp' ]] ; then

    shapefile="${isdir}/shapefiles/${basin}/${basin}_${option}.json"
    columnID='id'

else

    # look if HRU shapefile exists
    shapefile="${isdir}/shapefiles/${basin}/${basin}_${option}_hru"
    shapefile_zip="${shapefile}.zip"

    if [ ! -e  ${shapefile} ] ; then

	if [ -e ${shapefile_zip} ] ; then

	    # just not unzipped yet

	    cd "${isdir}/shapefiles/${basin}/"
	    unzip "${shapefile_zip}"
	    cd "${isdir}"

	else

	    # needs to be created


	    # unzip raw
	    if [ -e "${isdir}/shapefiles/${basin}/${basin}_${option}.zip" ] ; then
		cd "${isdir}/shapefiles/${basin}/"
		unzip "${basin}_${option}.zip"
		cd "${isdir}"
	    fi
	    shapefile_raw="${isdir}/shapefiles/${basin}/${basin}_${option}.shp"

	    # create shapefile with HRU columns
	    ravenpy generate-hrus-from-routing-product -o ${shapefile} ${shapefile_raw}

	    # # cleanup unzipped raw shapefiles
	    # rm "${isdir}/shapefiles/${basin}/${basin}_${option}.cpg"
	    # rm "${isdir}/shapefiles/${basin}/${basin}_${option}.dbf"
	    # rm "${isdir}/shapefiles/${basin}/${basin}_${option}.prj"
	    # rm "${isdir}/shapefiles/${basin}/${basin}_${option}.shp"
	    # rm "${isdir}/shapefiles/${basin}/${basin}_${option}.shx"

	    # zip new HRU shapefiles
	    cd "${isdir}/shapefiles/${basin}/"
	    zip -r "${basin}_${option}_hru.zip" ${basin}_${option}_hru/*.*
	    cd "${isdir}"

	fi

    fi

    #shapefile="${isdir}/shapefiles/${basin}/${basin}_${option}_hru/${basin}_${option}_hru.shp"
    shapefile="${isdir}/shapefiles/${basin}/${basin}_${option}_hru/${basin}_${option}_hru.shp"
    columnID='HRU_ID'

fi


if [ ! -e ${donefile} ] ; then

    # donefile does not exist but weights file does --> something happened while producing weights file --> remove and start over
    if [ -e ${outfile} ] ; then
	rm ${outfile}
    fi

    python additional_processing/derive_grid_weights.py -i ${infile} -d ${dimname} -v ${varname} -r ${shapefile} -b ${basin} -o ${outfile} -a  -c ${columnID}
    touch ${donefile}

fi


# cleanup unzipped files HRU shapefiles
if [[ ${option} == 'ds' ]] ; then

    rm -r "${isdir}/shapefiles/${basin}/${basin}_${option}_hru"

fi

exit 0
