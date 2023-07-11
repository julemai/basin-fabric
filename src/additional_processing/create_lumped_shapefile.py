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
#
# run:
#    python create_lumped_shapefile.py -i ../../data_in/shapefiles/02NE011/02NE011_ds -o ../../data_in/shapefiles/02NE011/02NE011_lp

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/../lib')

import argparse
import geopandas as gpd
from   shapely.ops import cascaded_union
from   coords2shapefile import coords2shapefile
import json


shapefile_ds  = '../../data_in/shapefiles/02NE011/02NE011_ds'
shapefile_lp  = '../../data_in/shapefiles/02NE011/02NE011_lp'


parser      = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
              description='''Derives basin attributes for given shapefile (extracted from routing product)''')
parser.add_argument('-i', '--shapefile_ds', action='store',
                    default=shapefile_ds, dest='shapefile_ds', metavar='shapefile_ds', nargs=1,
                    help='Shapefile for gauge ID. File extracted from routing product.')
parser.add_argument('-o', '--shapefile_lp', action='store',
                    default=shapefile_lp, dest='shapefile_lp', metavar='shapefile_lp',nargs=1,
                    help='File that contains basin names and location of gauge.')

args          = parser.parse_args()
shapefile_ds  = args.shapefile_ds[0]
shapefile_lp  = args.shapefile_lp[0]


# print("")

basin_id = shapefile_ds.split('/')[-2]


# ---------------------------
# merge all shapes and get mean centroid
# ---------------------------
# some projection IDs
CRS_LLDEG = 4326  # EPSG id of lat/lon (deg) coordinate reference system (CRS)

shape_subbasins = gpd.read_file(shapefile_ds+'.shp')
shape_subbasins_CRS_LLDEG = shape_subbasins.to_crs( crs=CRS_LLDEG )      # for landcover

# list of all polygons to merge
polygons_CRS_LLDEG = []
nshapes = len(shape_subbasins_CRS_LLDEG)
print("Shapefile contains {} features.".format(nshapes) )

for ishape in range(nshapes):

    if shape_subbasins_CRS_LLDEG.iloc[ishape]['geometry'].type == 'MultiPolygon':
        npoly = len(shape_subbasins_CRS_LLDEG.iloc[ishape]['geometry'])
        for ipoly in range(npoly):
            polygons_CRS_LLDEG.append(shape_subbasins_CRS_LLDEG.iloc[ishape]['geometry'][ipoly])
    else:
        polygons_CRS_LLDEG.append(shape_subbasins_CRS_LLDEG.iloc[ishape]['geometry'])



# merge
poly_union_CRS_LLDEG = gpd.GeoSeries(cascaded_union(polygons_CRS_LLDEG))[0].buffer(0.0)  # is a DataFrame but we want only the geometry part

if poly_union_CRS_LLDEG.geom_type == 'MultiPolygon':
    maxlen = 0
    imaxlen = -1
    for ipoly in range(len(poly_union_CRS_LLDEG)):
        nn = len(poly_union_CRS_LLDEG[ipoly].exterior.coords[:-1])
        if nn > maxlen:
            maxlen = nn
            imaxlen = ipoly
    coords = poly_union_CRS_LLDEG[imaxlen].exterior.coords[:-1]
elif poly_union_CRS_LLDEG.geom_type == 'Polygon':
    coords = poly_union_CRS_LLDEG.exterior.coords[:-1]
else:
    raise ValueError("Not sure what to do for geom_type '{}'!".format(poly_union_CRS_LLDEG.geom_type))

# write shapefile (of longest polygon)
coords2shapefile(shapefile_lp,coords)

# write as GeoJSON
shape_subbasins = gpd.read_file(shapefile_lp+'.shp')  # is a GeoPandas DataFrame
json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
with open(shapefile_lp+".json", "w") as outfile:
    json.dump(json_dict, outfile)
