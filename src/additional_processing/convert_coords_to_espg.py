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


def convert_coords_to_espg(shapefile_in,shapefile_out,espg=4326):

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

    Returns
    -------
    None

    """

    with fiona.open(shapefile_in) as shp_in:
        shapefile_in_crs = shp_in.crs
        shapes = shp_in[0]['geometry']

        # transform to requested CRS
        shapes = transform.transform_geom(shapefile_in_crs, {'init': 'epsg:'+str(espg)}, shapes)

        # pick longest shape
        nshapes = len(shapes.coordinates)
        if nshapes > 1:
            lens = [ len(ii) for ii in shapes.coordinates ]
            idx_longest = np.argmax(lens)
            print('More than one shape found in file (nshapes={}, len={}). Saving only longest one (idx={},len={}).'.format(nshapes,lens,idx_longest,lens[idx_longest]))
        else:
            idx_longest = 0
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


    print('Saved data to: {}.[dbf,prj,shp,shx]'.format(shapefile_out))


    return

if __name__ == '__main__':
    # import doctest
    # doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    import argparse

    shapefile_in  = None # '../WQ_station_list/20230612_Wei_selected_US_sites_shapefile/b_01116500.shp'
    shapefile_out = None # 'polygon'   # don't use any file ending here
    espg          = 4326

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

    args          = parser.parse_args()
    shapefile_in  = args.shapefile_in
    shapefile_out = args.shapefile_out
    espg          = args.espg

    if shapefile_in is None:
        raise ValueError('convert_coords_to_espg: Input shapefile (-i) is mandatory.')
    if shapefile_out is None:
        raise ValueError('convert_coords_to_espg: Output shapefile (-o) is mandatory.')

    convert_coords_to_espg(shapefile_in, shapefile_out, espg=espg)
