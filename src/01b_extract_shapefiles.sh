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
# ./01_extract_shapefiles.sh


set -e

#pyenv activate ravenpy



basins=$( cat WQ_station_list/WQstations_100obs_TP_SRP.txt | cut -d ';' -f 1 | grep ^1601840900[0-9] )
nbasins=$( cat WQ_station_list/WQstations_100obs_TP_SRP.txt | cut -d ';' -f 1 | grep ^[0-9] | wc -l )
regions=$( \ls Ontario_Routing_Product/drainage_region_*_v1-0/finalcat_info_v1-0.shp )

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"

    # create directory
    if [ ! -e shapefiles/${bb} ] ; then
	mkdir shapefiles/${bb}
    fi

    # search all files
    for rr in ${regions} ; do

	# check if basin is contained
	gauge_shapefile=$( echo ${rr} | rev | cut -d '/' -f 2- | rev )
	gauge_shapefile=$( echo ${gauge_shapefile}'/obs_gauges_v1-0.shp' )  # this one is just way smaller and faster to check
	python additional_processing/is_shp_containing_station.py -i ${gauge_shapefile} -a Obs_NM -b ${bb} > tmp.tmp
	basin=$( cat tmp.tmp )

	# extract
	if [[ ${basin} = 'One found:'* ]] ; then
	    basin=$( echo ${basin} | cut -d ':' -f 2 )  # get the basin ID found; can be "03003000202&02FB010" or "03003000202"
	    basin=$( echo ${basin} )
	    set +e
	    ravenpy collect-subbasins-upstream-of-gauge ${rr} ${basin} -o shapefiles/${bb}/${bb}_ds.shp
	    set -e
	fi
    done

    # if folder is empty --> cleanup since basin not found in RP
    if [ ! "$( \ls -A shapefiles/${bb} )" ] ; then
	rm -r shapefiles/${bb}
    fi

    cc=$(( cc+1 ))

done

exit 0
