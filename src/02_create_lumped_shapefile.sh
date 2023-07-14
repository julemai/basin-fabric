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
# ./02_create_lumped_shapefile.sh -s Wisconsin
# ./02_create_lumped_shapefile.sh -s Great-Lakes


set -ex

prog=$0
pprog=$(basename ${prog})
dprog=$(dirname ${prog})
isdir=${PWD}
pid=$$


case_study="None"
while getopts "hs:" Option ; do
    case ${Option} in
        h) usage 1>&2; exit 0;;
        s) case_study="${OPTARG}";;
        *) printf "Error ${pprog}: unimplemented option.\n\n";  usage 1>&2; exit 1;;
    esac
done
shift $((${OPTIND} - 1))

# Check if case_study is given
if [[ ${case_study} == 'None' ]] ; then
    printf "Error ${pprog}: Case study (-s) must be given.\n"
    exit 1
fi
case ${case_study} in
    'Wisconsin') ok='True' ;;
    'Great-Lakes') ok='True' ;;
    *) printf "Error ${pprog}: Option (-s) needs to be one of the following: 'Wisconsin', 'Great-Lakes'.\n\n";  usage 1>&2; exit 1;;
esac



if [[ ${case_study} == 'Great-Lakes' ]] ; then
    # Great Lakes
    region_tag='Great_Lakes_watersheds'
else
    if [[ ${case_study} == 'Wisconsin' ]] ; then
	# Wisconsin
	region_tag='Wisconsin_waterheds'
    else
	echo "Error ${pprog}: Option (-s) needs to be one of the following: 'Wisconsin', 'Great-Lakes'.\n\n"
	exit 1
    fi
fi


basins=$(  \ls -d ${dprog}/../regions/${region_tag}/shapefiles/[0-9]* | rev | cut -d '/' -f 1 | rev )
nbasins=$( \ls -d ${dprog}/../regions/${region_tag}/shapefiles/[0-9]* | rev | cut -d '/' -f 1 | rev | wc -l )

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"
    python additional_processing/create_lumped_shapefile.py -i ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_ds -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp
    echo "Wrote: ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp"

    cc=$(( cc+1 ))

done

exit 0
