#!/bin/bash

# Copyright 2022 Juliane Mai - juliane.mai(at)uwaterloo.ca
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
# pyenv activate ravenpy
# ./01_extract_shapefiles.sh -s wisconsin-lewis
# ./01_extract_shapefiles.sh -s ontario-zhi


set -ex

prog=$0
pprog=$(basename ${prog})
dprog=$(dirname ${prog})
isdir=${PWD}
pid=$$

case_study="None"
while getopts "hs:" Option ; do
    case ${Option} in
        h) exit 0;;
        s) case_study="${OPTARG}";;
        *) printf "Error ${pprog}: unimplemented option.\n\n";  exit 1;;
    esac
done
shift $((${OPTIND} - 1))

# Check if case_study is given
if [[ ${case_study} == 'None' ]] ; then
    printf "Error ${pprog}: Case study (-s) must be given.\n"
    exit 1
fi
case ${case_study} in
    'wisconsin-lewis') ok='True' ;;
    'ontario-zhi') ok='True' ;;
    *) printf "Error ${pprog}: Option (-s) needs to be one of the following: 'wisconsin-lewis', 'ontario-zhi'.\n\n";  exit 1;;
esac


if [[ ${case_study} == 'ontario-zhi' ]] ; then
    # Ontario
    region_tag='ontario-zhi'
    version='1-0'
    regions=$( \ls ${dprog}/../data/routing/Ontario_Routing_Product/drainage_region_*_v${version}/finalcat_info_v${version}.shp )

else
    if [[ ${case_study} == 'wisconsin-lewis' ]] ; then
	# wisconsin-lewis
	region_tag='wisconsin-lewis'
	version='2-1'
	regions=$( \ls ${dprog}/../data/routing/North_American_routing_product/drainage_region_*_v${version}/finalcat_info_v${version}.shp )
    else
	echo "Error ${pprog}: Option (-s) needs to be one of the following: 'wisconsin-lewis', 'ontario-zhi'.\n\n"
	exit 1
    fi
fi

basins=$(  cat ${dprog}/../regions/${region_tag}/basins.csv | cut -d ',' -f 1 | grep ^[0-9] )
nbasins=$( cat ${dprog}/../regions/${region_tag}/basins.csv | cut -d ',' -f 1 | grep ^[0-9] | wc -l )


# create directory
if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles/ ] ; then
    mkdir ${dprog}/../regions/${region_tag}/shapefiles/
fi

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"

    # create directory
    if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles/${bb} ] ; then
	mkdir ${dprog}/../regions/${region_tag}/shapefiles/${bb}
    fi

    # search all files
    for rr in ${regions} ; do

	if [[ ${case_study} == 'ontario-zhi' ]] ; then
	    # Ontario
	    # check if basin is contained
	    gauge_shapefile=$( echo ${rr} | rev | cut -d '/' -f 2- | rev )
	    gauge_shapefile=$( echo ${gauge_shapefile}'/obs_gauges_v1-0.shp' )  # this one is just way smaller and faster to check
	    python additional_processing/is_shp_containing_station.py -i ${gauge_shapefile} -a Obs_NM -b ${bb} > tmp.tmp
	    basin=$( cat tmp.tmp )
	    rm tmp.tmp
	else
	    if [[ ${case_study} == 'wisconsin-lewis' ]] ; then
		# wisconsin-lewis
		# check if basin is contained
		gauge_shapefile=$( echo ${rr} | rev | cut -d '/' -f 2- | rev )
		# this one is just way smaller and faster to check --> but has no 'HyLakeId' only 'Obs_NM'
		#gauge_shapefile=$( echo "${gauge_shapefile}/obs_gauges_v${version}.shp" )
		gauge_shapefile=$( echo ${rr} )
		python additional_processing/is_shp_containing_station.py -i ${gauge_shapefile} -a HyLakeId -b ${bb} > tmp.tmp
		basin=$( cat tmp.tmp )
		rm tmp.tmp
	    else
		echo "Error ${pprog}: Option (-s) needs to be one of the following: 'wisconsin-lewis', 'ontario-zhi'.\n\n"
		exit 1
	    fi
	fi

	# extract
	if [[ ${basin} = 'One found:'* ]] ; then
	    basin=$( echo ${basin} | cut -d ':' -f 2 )  # get the basin ID found; can be "03003000202&02FB010" or "03003000202"
	    basin=$( echo ${basin} )
	    set +e
	    if [[ ${case_study} == 'ontario-zhi' ]] ; then
		ravenpy collect-subbasins-upstream-of-gauge ${rr} ${basin} -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_ds.shp
	    else
		if [[ ${case_study} == 'wisconsin-lewis' ]] ; then
		    ravenpy collect-subbasins-upstream-of-gauge ${rr} ${basin} -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_ds.shp -a 'HyLakeId'
		else
		    echo "Error ${pprog}: Option (-s) needs to be one of the following: 'wisconsin-lewis', 'ontario-zhi'.\n\n"
		    exit 1
		fi
	    fi
	    set -e
	fi
    done

    # if folder is empty --> cleanup since basin not found in RP
    if [ ! "$( \ls -A ${dprog}/../regions/${region_tag}/shapefiles/${bb} )" ] ; then
	rm -r ${dprog}/../regions/${region_tag}/shapefiles/${bb}
    fi

    cc=$(( cc+1 ))

done

exit 0
