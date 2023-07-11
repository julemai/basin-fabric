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
#    python build_routing_model.py -b 03003000202

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/../lib')

import argparse
from   pathlib     import Path
from   sys         import platform
import shutil

from setup_model import setup_raven
from parse_model import parse_raven_model_paras
from parse_model import parse_raven_model_props
from parse_model import parse_raven_model_dates
from parse_model import parse_raven_model_files


basin     = None
parser    = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
              description='''Builds a routing-only model for given basin''')
parser.add_argument('-b', '--basin', action='store',
                    default=basin, dest='basin', metavar='basin',
                    help='Basin ID to build routing model for. Default: None.')
args      = parser.parse_args()
basin     = args.basin

if basin is None:
    raise ValueError('Basin (-b) needs to be specified.')





model_id     = 'routing_v21'
inputfiles   = dir_path+'/../routing_model_reference/raven_routing_v21.rv'
outputfolder = dir_path+'/../routing_model_basins/{}/raven_routing_v21'.format(basin)
routinginfo  = dir_path+'/../shapefiles/{}/{}_ds_hru/{}_ds_hru.shp'.format(basin,basin,basin)


simcal_period = ['2000-01-02', '2018-01-01']   # (15 years + 2 years warmup)
cal_period    = ['2001-01-01', '2017-12-31']   # (15 years; one day less otherwise Raven complains)

calibration_metric = 'KLING_GUPTA'
metric_multiplier = -1.0

mode = 'distributed'

# Make sure output directory exists
os.makedirs( Path(outputfolder), exist_ok=True )

# Set executables
dict_exe = {}
if platform == "linux" or platform == "linux2":
    # linux
    dict_exe['ostrich'] = dir_path+'/../executables/OstrichGCC_20171219_Linux.exe'
    dict_exe['raven']   = outputfolder+'/RavenExecutableLinux_v3.6n.exe'
    shutil.copy( dir_path+'/../executables/RavenExecutableLinux_v3.6n.exe', outputfolder+'/RavenExecutableLinux_v3.6n.exe' )
elif platform == "darwin":
    # OS X
    dict_exe['ostrich'] = dir_path+'/../executables/OstrichGCC_20171219_MacOS.exe'
    dict_exe['raven']   = outputfolder+'/RavenExecutableMacOS_v3.6n.exe'
    shutil.copy( dir_path+'/../executables/RavenExecutableMacOS_v3.6n.exe', outputfolder+'/RavenExecutableMacOS_v3.6n.exe' )
elif platform == "win64":
    # Windows...
    dict_exe['ostrich'] = dir_path+'/../executables/OstrichGCC_20171219_Windows.exe'
    dict_exe['raven']   = outputfolder+'/RavenExecutableWin64_v3.6n.exe'
    shutil.copy( dir_path+'/../executables/RavenExecutableWin64_v3.6n.exe', outputfolder+'/RavenExecutableWin64_v3.6n.exe' )
dict_exe['raven_path_adjust'] = '..'

# Parse for raven parameters
dict_paras = parse_raven_model_paras(inputfiles=inputfiles,model_id=model_id+'',routing=routinginfo)
#dict_paras = { dd:dd for dd in dict_paras }  # only names no vars

# Set some properties
dict_props = {}
dict_props['id']   =  basin
dict_props['name'] =  'unknown'

# parse some properties
dict_props_tmp = parse_raven_model_props(inputfiles=inputfiles,model_id=model_id+'_lumped',basin_id=dict_props['id'],basin_name=dict_props['name'],routing=routinginfo)

# add some properties that are only parsed
dict_props['Evaporation'] = dict_props_tmp['Evaporation']
dict_props['Routing']     = dict_props_tmp['Routing']

# overwrite properties that are actually distributed
if (mode == 'distributed'):
    dict_props['rbasin_id']   = dict_props_tmp['rbasin_id']
    dict_props['lat_deg']     = dict_props_tmp['lat_deg']
    dict_props['lon_deg']     = dict_props_tmp['lon_deg']
    dict_props['area_km2']    = dict_props_tmp['area_km2']
    dict_props['elevation_m'] = dict_props_tmp['elevation_m']
    dict_props['slope_deg']   = dict_props_tmp['slope_deg']
    dict_props['aspect_deg']  = dict_props_tmp['aspect_deg']

# Set dates
dict_dates = {}
dict_dates['simstart']   = simcal_period[0]
dict_dates['simend']     = simcal_period[1]
dict_dates['evaluation'] = ':EvaluationPeriod Period_01 '+cal_period[0]+' '+cal_period[1]

if mode == 'distributed':
    shortmode = 'ds'
elif mode == 'lumped':
    shortmode = 'lp'
else:
    raise ValueError("Mode (-d) needs to be on of the following ['lumped', 'distributed'] but is set to {}.".format(mode))

# set path of forcings/observations (maybe copy some files if run in tmpdir)
forcing_path = dir_path+'/../shapefiles/'+basin

# set filenames
dict_files = {}
dict_files['forcing'] = {}
dict_files['forcing']['PRECIP'] = {}
dict_files['forcing']['TEMP_DAILY_AVE'] = {}
dict_files['forcing']['TEMP_DAILY_MIN'] = {}
dict_files['forcing']['TEMP_DAILY_MAX'] = {}
dict_files['type']                                      = 'nc'
dict_files['qobs']                                      = forcing_path+'/model_basin_streamflow.rvt'
if Path(dict_files['qobs']).exists():
    dict_files['redirect_qobs'] = ':RedirectToFile {}'.format(dict_files['qobs'])
else:
    dict_files['redirect_qobs'] = "#:RedirectToFile # no streamflow observations found"

dict_files['forcing']['PRECIP']['filename']             = forcing_path+'/'+basin+'_agg_ERA5_Land_'+shortmode+'_ro.nc'
dict_files['forcing']['PRECIP']['varname']              = 'ro'
dict_files['forcing']['PRECIP']['dimname']              = ['nHRU', 'time']
dict_files['forcing']['PRECIP']['transform_a']          = '24000.0'  # ?????????????? I THOUGHT 1000 [m --> mm]
dict_files['forcing']['PRECIP']['transform_b']          = '0.0'
dict_files['forcing']['PRECIP']['timeshift']            = '0.0'
dict_files['forcing']['PRECIP']['gridweights']          = forcing_path+'/'+basin+'_gridweights_ERA5_Land_'+shortmode+'_aggregated.rvt'

dict_files['forcing']['TEMP_DAILY_AVE']['filename']     = forcing_path+'/'+basin+'_agg_ERA5_Land_'+shortmode+'_ro.nc'
dict_files['forcing']['TEMP_DAILY_AVE']['varname']      = 'ro'
dict_files['forcing']['TEMP_DAILY_AVE']['dimname']      = ['nHRU', 'time']
dict_files['forcing']['TEMP_DAILY_AVE']['transform_a']  = '0.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_AVE']['transform_b']  = '5.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_AVE']['timeshift']    = '0.0'
dict_files['forcing']['TEMP_DAILY_AVE']['gridweights']  = forcing_path+'/'+basin+'_gridweights_ERA5_Land_'+shortmode+'_aggregated.rvt'

dict_files['forcing']['TEMP_DAILY_MIN']['filename']     = forcing_path+'/'+basin+'_agg_ERA5_Land_'+shortmode+'_ro.nc'
dict_files['forcing']['TEMP_DAILY_MIN']['varname']      = 'ro'
dict_files['forcing']['TEMP_DAILY_MIN']['dimname']      = ['nHRU', 'time']
dict_files['forcing']['TEMP_DAILY_MIN']['transform_a']  = '0.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_MIN']['transform_b']  = '5.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_MIN']['timeshift']    = '0.0'
dict_files['forcing']['TEMP_DAILY_MIN']['gridweights']  = forcing_path+'/'+basin+'_gridweights_ERA5_Land_'+shortmode+'_aggregated.rvt'

dict_files['forcing']['TEMP_DAILY_MAX']['filename']     = forcing_path+'/'+basin+'_agg_ERA5_Land_'+shortmode+'_ro.nc'
dict_files['forcing']['TEMP_DAILY_MAX']['varname']      = 'ro'
dict_files['forcing']['TEMP_DAILY_MAX']['dimname']      = ['nHRU', 'time']
dict_files['forcing']['TEMP_DAILY_MAX']['transform_a']  = '0.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_MAX']['transform_b']  = '5.0'    # WE DO NOT HAVE TEMPERATURE!!!!
dict_files['forcing']['TEMP_DAILY_MAX']['timeshift']    = '0.0'
dict_files['forcing']['TEMP_DAILY_MAX']['gridweights']  = forcing_path+'/'+basin+'_gridweights_ERA5_Land_'+shortmode+'_aggregated.rvt'

# Setup Raven
setup_folder = setup_raven(
    model_id=model_id,
    dict_paras=dict_paras,
    dict_props=dict_props,
    dict_dates=dict_dates,
    dict_files=dict_files,
    # dict_exe=dict_exe,
    routing=routinginfo,
    outputfolder=outputfolder,
    metric=calibration_metric,
    #cal_method='dds',
    #budget=budget,
    #seed=None,
    #calmode=True
    )
