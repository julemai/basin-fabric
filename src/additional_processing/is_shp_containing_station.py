#!/usr/bin/env python
from __future__ import print_function

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

# checks if station (-b) is in shapefile (-i) specified under attribute (-a). multiple can be
# specified in attribute using &, e.g. "03003000202&02FB010". will return name of attribute in
# shapefile. helpful if this basin is supposed to get extracted
#
# run:
#    python is_shp_containing_station.py -i ../Ontario_Routing_Product/drainage_region_SW_v1-0/finalcat_info_v1-0.shp -a Obs_NM -b 03003000202

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/../lib')

import argparse
import geopandas as gpd
import numpy     as np


shapefile = None
attribute = 'obs_NM'
basin     = None


parser      = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
              description='''Derives basin attributes for given shapefile (extracted from routing product)''')
parser.add_argument('-i', '--shapefile', action='store',
                    default=shapefile, dest='shapefile', metavar='shapefile',
                    help='Shapefile from routing product. Default: None.')
parser.add_argument('-a', '--attribute', action='store',
                    default=attribute, dest='attribute', metavar='attribute',
                    help='Attribute in shapefile to check for basin ID. Default: Obs_NM.')
parser.add_argument('-b', '--basin', action='store',
                    default=basin, dest='basin', metavar='basin',
                    help='Basin ID to look for in shapefile. Default: None.')

args      = parser.parse_args()
shapefile = args.shapefile
attribute = args.attribute
basin     = args.basin

if shapefile is None:
    raise ValueError('Shapefile (-i) needs to be specified.')

if basin is None:
    raise ValueError('Basin (-b) needs to be specified.')


shapefile_data = gpd.read_file(shapefile)
all_basins     = np.array(shapefile_data[attribute])[np.where( np.array(shapefile_data[attribute]) != np.array(None) )]
all_basins     = [ str(bb).strip() for bb in all_basins ]

# print("is_shp_containing_station: all basins found = {}".format(all_basins))

basin_id_found = [ bb for bb in all_basins if basin in bb.split('&') ]

if len(basin_id_found) == 1:
    print('One found: {}'.format(basin_id_found[0]))
elif len(basin_id_found) == 0:
    print('None found')
else:
    print('Multiple found: {}'.format(basin_id_found))
