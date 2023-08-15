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

import fiona
from   fiona import transform
import shapefile
import numpy as np
import sys
import geopandas as gpd
import json


def convert_coords_to_espg(shapefile_in,shapefile_out,espg=4326,extract=None):

    """
    Converts given shapefile into shapefile with given ESPG of a CRS.

    Parameters
    ----------
    shapefile_in: str
        Name of the shapefile (e.g., test.shp).

    shapefile_out: str
        Name of the shapefile (without any extension). Files that will be produced are:
        <filename>.dbf
        <filename>.prj
        <filename>.shp
        <filename>.shx
        Zip these four files to upload to CaSPAr.

    espg: integer
        ESPG of coordinate reference system (CRS).

    extract: string in format "<shapefile_attribute_key>=<ID>"
        will extract only shape where shapefile_attribute_key=ID specified

    Returns
    -------
    None

    """

    attribute_key = extract.split('=')[0]
    attribute_val = extract.split('=')[1]
    attribute_type = 'int'


    # open file
    with fiona.open(shapefile_in) as shp_in:

        # get crs
        shapefile_in_crs = shp_in.crs

        # extract shape of interest
        if not(extract is None):
            if attribute_type == 'int':
                shape_idx = int( np.where(np.array([ ii['properties'][attribute_key] for ii in shp_in ])==int(attribute_val))[0][0] )
            else:
                raise ValueError('Implement other attribute type.')
            print('Shape to extract: {}'.format(shape_idx))
        else:
            shape_idx = 0
        shapes = shp_in[shape_idx]['geometry']

    # transform to requested CRS
    shapes = transform.transform_geom(shapefile_in_crs, {'init': 'epsg:'+str(espg)}, shapes)

    # pick longest shape
    nshapes = len(shapes.coordinates)
    if nshapes > 1:
        lens = np.array([ len(ii) for ii in shapes.coordinates ])
        if np.all( lens == 1):
            one_more_dim = True
            lens = np.array([ len(ii[0]) for ii in shapes.coordinates ])
        else:
            one_more_dim = False
        idx_longest = np.argmax(lens)
        print('More than one shape found in file (nshapes={}, len={}). Saving only longest one (idx={},len={}).'.format(nshapes,lens,idx_longest,lens[idx_longest]))
    else:
        one_more_dim = False
        idx_longest = 0

    if one_more_dim:
        coords = shapes.coordinates[idx_longest][0]
    else:
        coords = shapes.coordinates[idx_longest]

    # make list; not tuple
    coords = [ list(ii) for ii in coords ]

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
        w.save(shapefile_out)
    else:
        # ------------------------
        # Create a polygon shapefile
        # ------------------------
        # Found under:
        #     https://code.google.com/archive/p/pyshp/
        w = shapefile.Writer(target=shapefile_out)

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
    prj = open("%s.prj" % shapefile_out, "w")
    epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
    prj.write(epsg)
    prj.close()

    # ------------------------
    # write as GeoJSON
    # ------------------------
    shape_subbasins = gpd.read_file(shapefile_out+'.shp')  # is a GeoPandas DataFrame
    json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
    with open(shapefile_out+".json", "w") as outfile:
        json.dump(json_dict, outfile)



    print('Saved data to: {}.[dbf,prj,shp,shx,json]'.format(shapefile_out))


    return

if __name__ == '__main__':
    # import doctest
    # doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    import argparse

    shapefile_in  = None # '../WQ_station_list/20230612_Wei_selected_US_sites_shapefile/b_01116500.shp'
    shapefile_out = None # 'polygon'   # don't use any file ending here
    espg          = 4326
    extract       = None

    parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Convert shapefile into new CRS and save only longest shape.''')
    parser.add_argument('-i', '--shapefile_in', action='store',
                            default=shapefile_in, dest='shapefile_in', metavar='shapefile_in',
                            help='Name of input shapefile (with extension*.shp).')
    parser.add_argument('-o', '--shapefile_out', action='store',
                            default=shapefile_out, dest='shapefile_out', metavar='shapefile_out',
                            help='Name of output shapefile (without extension).')
    parser.add_argument('-e', '--espg', action='store',
                            default=espg, dest='espg', metavar='espg',
                            help='ESPG of coordinate reference system to convert to. Default: 4326.')
    parser.add_argument('-x', '--extract', action='store',
                            default=extract, dest='extract', metavar='extract',
                            help='Extract only shape where shapefile_attribute_key=ID specified. String needs to be in format: "<shapefile_attribute_key>=<ID>". Default: None.')

    args          = parser.parse_args()
    shapefile_in  = args.shapefile_in
    shapefile_out = args.shapefile_out
    espg          = args.espg
    extract       = args.extract

    if shapefile_in is None:
        raise ValueError('convert_coords_to_espg: Input shapefile (-i) is mandatory.')
    if shapefile_out is None:
        raise ValueError('convert_coords_to_espg: Output shapefile (-o) is mandatory.')



    convert_coords_to_espg(shapefile_in, shapefile_out, espg=espg, extract=extract)
