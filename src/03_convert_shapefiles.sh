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
# pyenv activate env-3.8.5-ravenpy-new
# ./03_convert_shapefiles.sh -s conus-zhi
# ./03_convert_shapefiles.sh -s grip-gl-mai


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
    'conus-zhi') ok='True' ;;
    'grip-gl-mai') ok='True' ;;
    *) printf "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai'.\n\n"; exit 1;;
esac


if [[ ${case_study} == 'conus-zhi' ]] ; then
    # conus-zhi
    region_tag='conus-zhi'

    basins=$(  \ls ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 )
    nbasins=$( \ls ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 | wc -l )
else
    if [[ ${case_study} == 'grip-gl-mai' ]] ; then
	# grip-gl-mai
	region_tag='grip-gl-mai'

	basins=$(  \ls ${dprog}/../regions/${region_tag}/shapefiles_raw/*/*.shp | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1 )
	nbasins=$( \ls ${dprog}/../regions/${region_tag}/shapefiles_raw/*/*.shp | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1 | wc -l )
    else
	echo "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai'.\n\n"
	exit 1
    fi
fi


# create directory
if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles ] ; then
    mkdir ${dprog}/../regions/${region_tag}/shapefiles
fi

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"

    # create directory
    if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles/${bb} ] ; then
    	mkdir ${dprog}/../regions/${region_tag}/shapefiles/${bb}
    fi

    if [[ ${case_study} == 'conus-zhi' ]] ; then
	# conus-zhi
	# convert Wei's shapefile with weird projection into standard one (add ESPG and save only longest feature)
	python additional_processing/convert_coords_to_espg.py \
	       -i ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_${bb}.shp \
	       -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
	       -e 4326
    else
	if [[ ${case_study} == 'grip-gl-mai' ]] ; then
	    # grip-gl-mai
	    # convert grip-gl-mai shapefile with into standard one (save only longest feature; add ESPG; but it's actually just a rename...)
	    python additional_processing/convert_coords_to_espg.py \
		   -i ${dprog}/../regions/${region_tag}/shapefiles_raw/${bb}/${bb}.shp \
		   -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
		   -e 4326
	else
	    echo "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai'.\n\n"
	    exit 1
	fi
    fi

    cc=$(( cc+1 ))

done

exit 0
