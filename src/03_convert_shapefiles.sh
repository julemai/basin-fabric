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
# ./01_convert_shapefiles.sh


set -e

#pyenv activate env-3.8.5-ravenpy-new

basins=$( \ls WQ_station_list/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 )
nbasins=$( \ls WQ_station_list/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 | wc -l )

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"

    # create directory
    if [ ! -e shapefiles/${bb} ] ; then
    	mkdir shapefiles/${bb}
    fi

    # convert Wei's shapefile with weird projection into standard one
    python additional_processing/convert_coords_to_espg.py -i WQ_station_list/20230612_Wei_selected_US_sites_shapefile/b_${bb}.shp -o shapefiles/${bb}/${bb}_lp -e 4326

    cc=$(( cc+1 ))

done

exit 0
