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
#    python get_time_zone.py -l 49.776333,-97.095902

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(dir_path+'/../lib')

import argparse
import datetime
import pytz
from timezonefinder import TimezoneFinder

def get_time_zone(lat,lon,silent=True):

    # :param lat: latitude  of the point in degree (90.0 to -90.0)
    # :param lon: longitude of the point in degree (-180.0 to 180.0)
    # :return     returns time offset in hours realtive to UTC

    # object creation
    obj = TimezoneFinder()

    # pass the longitude and latitude
    # in timezone_at and
    # it return time zone
    timezone_str = obj.timezone_at(lng=lon, lat=lat)

    if not(silent): print("Time zone:       ", timezone_str)

    timezone = pytz.timezone(timezone_str)
    dt = datetime.datetime.now()
    timezone_offset_obj = timezone.utcoffset(dt)
    timezone_offset_hrs = timezone_offset_obj.total_seconds()/60./60.

    if not(silent): print("Time offset (h): ", timezone_offset_hrs)

    return timezone_offset_hrs




if __name__ == '__main__':

    latlon_string   = '49.776333,-97.095902'   # somewhere around Winnipeg


    parser      = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                  description='''Extracts subdomain provided in shapefile (-s) from set of input NC files (-i) and merges them into one output NC file (-o).''')
    parser.add_argument('-l', '--latlon_string', action='store',
                        default=latlon_string, dest='latlon_string', metavar='latlon_string',
                        help='String of latitude and longitude; comma separated. E.g., "48.0,-70.0"')


    args           = parser.parse_args()
    latlon_string  = args.latlon_string
    lat = float(latlon_string.strip().split(',')[0])
    lon = float(latlon_string.strip().split(',')[1])


    timezone_offset_hrs = get_time_zone(lat,lon)
    print("Time offset (h): ", timezone_offset_hrs)
