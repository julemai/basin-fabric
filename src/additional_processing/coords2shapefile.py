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


"""

Converts list of coordinates (in degrees) to a shapefile that can be uploaded to CaSPAr.

Polygon does not need to be closed.

Requires shapefile package which can be installed using "pip install pyshp".
For further details see: https://code.google.com/archive/p/pyshp/

History
-------
Written,  JM, May 2020

"""

import shapefile
import sys


def coords2shapefile(filename,coords):

    """
    Converts given coordinates into shapefile that can be uploaded to CaSPAr.

    Parameters
    ----------
    filename: str
        Name of the shapefile (without any extension). Files that will be produced are:
        <filename>.dbf
        <filename>.prj
        <filename>.shp
        <filename>.shx
        Zip these four files to upload to CaSPAr.

    coords: array
        2-D Array of coordinates of a single polygon. CaSPAr does not support
        multiple polygons. Polygon does not need to be closed. The shapefile package is
        checking and copies automatically the first point to the end if polygon is not closed.
        Example:
        [[-123,50], [-118,40], [-118,44], [-113,44]]              # unclosed geometry
        [[-123,50], [-118,40], [-118,44], [-113,44],[-123,50]]    # closed geometry

    Returns
    -------
    None

    """

    # make sure coords is a list of lists
    coords = [ list(ii) for ii in coords ]

    # -----------------------
    # Check if polygon is clockwise:
    #       Use "shapefile.signed_area()" method to determine if a ring is clockwise or counter-clockwise
    #       Value >= 0 means the ring is counter-clockwise.
    #       Value <  0 means the ring is clockwise
    #       The value returned is also the area of the polygon.
    # -----------------------
    area = shapefile.signed_area(coords)

    if area >= 0:
        coords.reverse()    # transform counter-clockwise to clockwise

    if sys.version_info < (3,0,0):
        # ------------------------
        # Create a polygon shapefile
        # ------------------------
        # Found under:
        #     https://code.google.com/archive/p/pyshp/
        w = shapefile.Writer(shapefile.POLYGON)

        # an arrow-shaped polygon east of Vancouver, Seattle, and Portland
        w.poly([coords])
        w.field('FIRST_FLD','C','40')
        w.record('First','Polygon')
        w.save(filename)
    else:
        # ------------------------
        # Create a polygon shapefile
        # ------------------------
        # Found under:
        #     https://code.google.com/archive/p/pyshp/
        w = shapefile.Writer(target=filename)

        # an arrow-shaped polygon east of Vancouver, Seattle, and Portland
        w.poly([coords])
        w.field('FIRST_FLD','C','40')
        w.record('First','Polygon')
        w.close()


    # ------------------------
    # Write projection information
    # ------------------------
    # Found under:
    #     https://code.google.com/archive/p/pyshp/wikis/CreatePRJfiles.wiki
    prj = open("%s.prj" % filename, "w")
    epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
    prj.write(epsg)
    prj.close()

    return

if __name__ == '__main__':
    # import doctest
    # doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    coords = [[-123,50], [-118,40], [-118,44], [-113,44]]
    filename = 'polygon'   # don't use any file ending here

    coords2shapefile(filename,coords)


    
    # --------------------------------------------------------
    # duc8-camelo
    # --------------------------------------------------------

    
    # path_to_file = '../../regions/duc8-camelo/4326_HydrologyAnalyst_Basins.geojson'

    # import geojson
    # import geopandas as gpd
    # import json
    
    # with open(path_to_file) as f:
    #     gj = geojson.load(f)

    # nfeatures = len(gj['features'])
    # for ifeature in range(nfeatures):

    #     basin = gj['features'][ifeature]['properties']['id']
    #     filename = '../../regions/duc8-camelo/shapefiles/{}/{}_lp'.format(basin,basin)

    #     print('Working on basin {}'.format(basin))

    #     # write shapefile
    #     coords = gj['features'][ifeature]['geometry']['coordinates'][0]
    #     coords2shapefile(filename,coords)

    #     # write as GeoJSON
    #     shape_subbasins = gpd.read_file(filename+'.shp')  # is a GeoPandas DataFrame
    #     json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
    #     with open(filename+".json", "w") as outfile:
    #         json.dump(json_dict, outfile)




    # --------------------------------------------------------
    # wrtdsk-mai
    # --------------------------------------------------------

    # path_to_file_shp    = '../../regions/wrtdsk-mai/dataset-03_download_Point_geometry.js'
    # path_to_file_latlon = '../../regions/wrtdsk-mai/dataset-03_download_Point.js'

    # import geojson
    # import geopandas as gpd
    # import json
    # import numpy as np
    # import math
    # import pandas as pd

    # def handle_nan(val):
    #     if val == "NaN":
    #         return math.nan
    #     raise ValueError(f"Unexpected constant: {val}")

    # with open(path_to_file_shp) as ff1:
    #     gj = geojson.load(ff1)

    # with open(path_to_file_latlon) as ff2:
    #     gjll = geojson.load(ff2, parse_constant=handle_nan)
    # # array of ids for lookup
    # llids = np.array([ gjll['features'][ii]['properties']['id'] for ii in range(len(gjll['features'])) ])
        
    # nfeatures = len(gj['features'])

    # count_wo_shp_file = 0
    # count_w_shp_file = 0
    # dict_meta = {}
    # for ifeature in range(nfeatures):

    #     basin = gj['features'][ifeature]['properties']['id']
    #     filename = '../../regions/wrtdsk-mai/shapefiles/{}/{}_lp'.format(basin,basin)

    #     if gj['features'][ifeature]['properties']['area_km2_5070'] > 0.0:

    #         print('Working on basin {} ({} of {})'.format(basin,ifeature+1,nfeatures))

    #         # write shapefile
    #         coords = gj['features'][ifeature]['geometry']['coordinates'][0]
    #         coords2shapefile(filename,coords)

    #         # write as GeoJSON
    #         shape_subbasins = gpd.read_file(filename+'.shp')  # is a GeoPandas DataFrame
    #         json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
    #         with open(filename+".json", "w") as outfile:
    #             json.dump(json_dict, outfile)

    #         count_w_shp_file += 1

    #         idx = np.where(np.array(llids)==basin)[0]
    #         if len(idx) > 0:
    #             idx = idx[0]
    #             dict_meta[basin] = {  "id":    gjll['features'][idx]['properties']["id"],
    #                                   "name":  gjll['features'][idx]['properties']["name"].replace(',',';'),
    #                                   "lat":   gjll['features'][idx]['properties']["lat_deg_c"],
    #                                   "lon":   gjll['features'][idx]['properties']["lon_deg_c"],
    #                                   "obs_q": gjll['features'][idx]['properties']["station_q"]
    #                                 }

    #     else:

    #         print('Working on basin {} ({} of {}) --> discarded because shapefile not known'.format(basin,ifeature+1,nfeatures))

    #         count_wo_shp_file += 1

    # if len(dict_meta) != count_w_shp_file:
    #     raise ValueError('Number of basins we wrote shapefiles for does not match number of basins with metadata available.')

    # # convert to DataFrame
    # df = pd.DataFrame.from_dict(dict_meta, orient='index')

    # # reorder columns
    # df = df[['id', 'name', 'lat', 'lon', 'obs_q']]

    # # save to CSV
    # filename = "../../regions/wrtdsk-mai/basins.csv"
    # df.to_csv(filename, index=False)

    # print("Number of basins where we did not know shapefile (all US since Kim did not provide shapefiles: {}".format(count_wo_shp_file))
    # print("Number of basins with shapefile and other info available:                                      {}".format(count_w_shp_file))

    # print('')
    # print('Wrote: {}'.format(filename))
