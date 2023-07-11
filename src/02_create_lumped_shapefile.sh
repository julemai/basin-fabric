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
# ./02_create_lumped_shapefile.sh


set -e

basins=$( \ls -d shapefiles/[0-9]* | cut -d '/' -f 2 )
nbasins=$( \ls -d shapefiles/[0-9]* | wc -l )

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"
    python additional_processing/create_lumped_shapefile.py -i shapefiles/${bb}/${bb}_ds -o shapefiles/${bb}/${bb}_lp
    echo "Wrote: shapefiles/${bb}/${bb}_lp"

    cc=$(( cc+1 ))

done

exit 0
