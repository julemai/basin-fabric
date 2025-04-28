#!/usr/bin/env python
from __future__ import print_function

# Copyright 2023 Juliane Mai - contact[at]juliane-mai[dot]com
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

# pyenv activate env-3.8.5-ravenpy-new

# python 07_create_lumped_forcings.py -s ontario-zhi -b 03005400102 -f /Users/j6mai/Documents/Nandita/ontario-zhi/gridded_data/rdrs_v2/ -y mac

# takes 73.5 minutes
# python 07_create_lumped_forcings.py -s ontario-zhi -b 03005400102 -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2_grip-gl/ -y graham

# takes XXX minutes
# python 07_create_lumped_forcings.py -s ontario-zhi -b 03005400102 -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham


"""

Creates lumped forcings for all basins in a project (shapefiles) and list of netCDF files
containing variables (e.g., file for precipitation, temperature, and wind speed).


License
-------
This file is part of the Basin Fabric which contains scripts to
process data for basins, deriving attributes, processing forcings,
and setting up and training data-driven models.

The Basin Fabric code is free software: you can redistribute it
and/or modify it under the terms of the MIT License.

The Basin Fabric code library is distributed in the hope that it will
be useful,but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
License for more details.

You should have received a copy of the MIT License along with the
Basin Fabric code. If not, see
<https://github.com/julemai/basin-fabric/blob/main/LICENSE>.

Copyright 2023 Juliane Mai - juliane.mai@uwaterloo.ca


History
-------
Written,  JM, Jul 2023 - initial script

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse

case_study   = None
forcings     = None
basin        = None
system       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai'].")
parser.add_argument('-f', '--forcings', action='store', default=forcings, dest='forcings',
                    help="Name of folder containing forcings for a larger region (e.g., Great Lakes or North America).")
parser.add_argument('-b', '--basin', action='store', default=basin, dest='basin',
                    help="Name of basin to process. Shapefile in subfolder 'shapefile' is assumed to be named like this ID.")
parser.add_argument('-y', '--system', action='store', default=system, dest='system',
                    help="Name of system. Either 'graham' or 'mac'.")

args         = parser.parse_args()
case_study   = args.case_study
forcings     = args.forcings
basin        = args.basin
system       = args.system

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")

if (forcings is None):
    raise ValueError("Name of folder containing gridded forcings for larger domain (-f) must be specified.")


del parser, args


from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')




from   pathlib  import Path
from   datetime import datetime
import glob    as glob
import numpy   as np
import pandas  as pd
import xarray  as xr
import netCDF4 as nc
import subprocess
import os


if case_study == 'wisconsin-lewis':
    column_id = "FIRST_FLD"
    if system == 'mac':
        project_root = Path('/Users/j6mai/Documents/Nandita/wisconsin-lewis')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/wisconsin-lewis/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')
    dimname="rlon,rlat"
    varname="lon,lat"

elif case_study == 'ontario-zhi':
    column_id = "FIRST_FLD"
    if system == 'mac':
        project_root = Path('/Users/j6mai/Documents/Nandita/ontario-zhi')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/ontario-zhi/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'conus-zhi':
    column_id = "FIRST_FLD"
    if system == 'mac':
        project_root = Path('/Users/j6mai/Documents/Nandita/conus-zhi/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/conus-zhi/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'grip-gl-mai':
    column_id = "FIRST_FLD"
    if system == 'mac':
        project_root = Path('/Users/j6mai/Documents/GitHub/grip-gl-mai/data/shapefiles/great-lakes/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/grip-gl-mai/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'north-america-mai':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/north-america-mai/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'camels-us-newman':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/camels-us-newman/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'lake-erie-us-gaffney':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/lake-erie-us-gaffney/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'prairie-canada-mai':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/prairie-canada-mai/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'prairie-canada-downstream-mai':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/prairie-canada-downstream-mai/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')

elif case_study == 'wq-us-chang':
    column_id = "FIRST_FLD"
    if system == 'mac':
        raise ValueError('Do not know where to find data here.')
        project_root = Path('/Users/j6mai/Documents/GitHub/')
    elif system == 'graham':
        project_root = Path(str(Path(__file__).parent)+'/../regions/wq-us-chang/')
    else:
        raise ValueError('System not known. Specify a valid one with (-y) option.')
    
else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))


if (basin is None):
    raise ValueError("Basin to process. Shapefile of this basin is assumed to be found under {}/shapefiles/<basin>/<basin>_lp.shp.".format(project_root))

do_forcings       = True



if do_forcings:

    # 1- find all netcdf files in forcing folder
    filenames = np.sort( glob.glob(forcings+'/*.nc') )

    # 2- check they are consistent regarding lat/lon/time
    irlat = None
    irlon = None
    for ff in filenames[0:4]:
        print('Checking consistency of dimensions of file {}\n'.format(Path(ff).name))
        with nc.Dataset(ff) as iff:

           if (irlat is None):
               irlat = iff.dimensions['rlat'].size
           else:
               if ( iff.dimensions['rlat'].size != irlat ):
                   raise ValueError('rlat dimension of file {} is {} but is expected to be {}'.format(ff,iff.dimensions['rlat'].size,irlat))

           if (irlon is None):
               irlon = iff.dimensions['rlon'].size
           else:
               if ( iff.dimensions['rlon'].size != irlon ):
                   raise ValueError('rlon dimension of file {} is {} but is expected to be {}'.format(ff,iff.dimensions['rlon'].size,irlon))

    # 3- read grid of one file
    with nc.Dataset(filenames[0]) as iff:
        lat = iff['lat']
        lon = iff['lon']

    # 4- find shapefile
    shpfile = Path( project_root, 'shapefiles', basin, basin+'_lp.shp' )
    if not( shpfile.exists() ):
        raise ValueError('No shapefile found under {} for basin {}'.format(shpfile, basin))

    # 5- generate grid weights
    #    python additional_processing/derive_grid_weights.py-i ${infile} -d ${dimname} -v ${varname} -r ${shapefile} -b ${basin} -o ${outfile} -a  -c ${columnID}
    weightsfile = Path(project_root, 'forcings', basin, basin+'_gridweights_'+Path(filenames[0]).parent.name+'_lp.txt')

    # Make directory if does not exist
    if not os.path.exists(weightsfile.parent):
        os.makedirs(weightsfile.parent)

    if not( weightsfile.exists() ):

        if system == 'mac':
            pyenv = "/Users/j6mai/.pyenv/versions/env-3.8.5-ravenpy-new/bin/python"
        elif system == 'graham':
            pyenv = "/home/julemai/env-3.10/bin/python"
            pyenv = "/scratch/julemai/basin-fabric/env-3.11/bin/python"
            pyenv = "/project/6070465/julemai/basin-fabric/env-3.11/bin/python"
        else:
            raise ValueError('System not known. Specify a valid one with (-y) option.')

        subprocess.run([pyenv, "additional_processing/derive_grid_weights.py",
                        "-i", filenames[0],
                        "-d", "rlon,rlat",
                        "-v", "lon,lat",
                        "-r", shpfile,
                        "-b", basin,
                        "-o", weightsfile,
                        "-a",
                        "-c", column_id,
                        "-p", "4326"])
    else:
        print("Weightsfile existed. Will not be overwritten.\nFile = {}\n".format(weightsfile))

    # 6- extract lumped variables
    outfiles_agg = []
    outfile_merge = Path(project_root, 'forcings', basin, basin+'_agg_'+Path(filenames[0]).parent.name+'_lp.nc')

    for filename in filenames:

        print("Aggregating: {}".format(filename))

        # name of aggregated output file
        outfile_agg = Path(project_root, 'forcings', basin, basin+'_agg_'+Path(filename).parent.name+'_'+Path(filename).name+'_lp.nc')

        if not( outfile_agg.exists() or outfile_merge.exists() ):

            # 3d variables in input file
            with nc.Dataset(filename) as iff:
                ivars = list(iff.variables.keys())
                # ivars_3d = ' '.join([ ii for ii in ivars if len(iff[ii].dimensions) == 3 ])
                ivars_3d = [ ["--var-to-aggregate",ii] for ii in ivars if len(iff[ii].dimensions) == 3 ]
            ivars_3d = [ item for sublist in ivars_3d for item in sublist]

            # ravenpy aggregate-forcings-to-hrus --dim-names rlon rlat --var-to-aggregate "RDRS_v2_A_PR0_SFC" --output-nc-file ${outfile_prec} ${infile_prec} ${weights_file}
            args = ["ravenpy", "aggregate-forcings-to-hrus",
                                "--dim-names", "rlon", "rlat" ] + ivars_3d + [   # n times "--var-to-aggregate"
                                "--output-nc-file", outfile_agg,
                                filename,
                                weightsfile ]
            # print("args = ",args)
            subprocess.run(args)

            # make time UNLIMITED
            subprocess.run(["ncks", "--mk_rec_dmn", "time", outfile_agg, str(outfile_agg)+"_new.nc"])
            subprocess.run(["mv", str(outfile_agg)+"_new.nc", outfile_agg])

        else:
            if outfile_agg.exists():
                print("Aggregated file existed. Will not be overwritten.\nFile = {}\n".format(outfile_agg))
            else:
                print("Trying to aggregate but merged file already existed. Will not start producing aggregated file again.\nFile = {}\n".format(outfile_merge))

        outfiles_agg.append(outfile_agg)

    # 7- merge all files (individual variables and/or time periods) into one
    if not( outfile_merge.exists() ):

        # ds = xr.merge([ xr.open_dataset(ff) for ff in outfiles_agg ])
        ds = xr.open_mfdataset(outfiles_agg, engine='netcdf4')  # using dask; more efficient
        ds.to_netcdf(outfile_merge)

        # # testing
        # import glob as glob
        # import xarray as xr
        # outfiles_agg = list(np.sort(glob.glob('/scratch/julemai/basin-fabric/regions/wisconsin-lewis/forcings/1032267/1032267_agg_rdrs-v2.1_north-america_*_RDRS_v2.1_*.nc_lp.nc')))
        # outfile_merge='test-merge.nc'
        # ds = xr.open_mfdataset(outfiles_agg)
        # ds.to_netcdf(outfile_merge)

    else:
        print("Merged file existed. Will not be overwritten.\nFile = {}\n".format(outfile_merge))

    print('\n\nMerged file written: {}\n'.format(outfile_merge))




    # cd regions/wisconsin-lewis/forcings/
    # basins=$( \ls -d * )

    # for bb in $basins ; do echo "----------------" ; ff=$( \ls -latrh ${bb}/*.nc | tail -1 | rev | cut -d ' ' -f 1 | rev ) ; echo $ff ; done
    # for bb in $basins ; do echo "----------------" ; ff=$( \ls -latrh ${bb}/*.nc | tail -1 | rev | cut -d ' ' -f 1 | rev ) ; rm $ff ; done






    # POTENTIALLY HELPFUL

    # # (1) set time to proper string
    # #       time:units = "hours since 2000-1-1 12:00:00"     -->    time:units = "hours since 2000-01-01 12:00:00"
    # ncatted -O -a units,time,o,c,"hours since 2000-01-01 12:00:00" ${outfile_prec}
    # ncatted -O -a units,time,o,c,"hours since 2000-01-01 12:00:00" ${outfile_temp}

    # # (2) purge history
    # # (2a) delete super long "history_of_appended_files"
    # ncatted -O -a history_of_appended_files,global,d,, ${outfile_prec}
    # ncatted -O -a history_of_appended_files,global,d,, ${outfile_temp}
    # # (2b) set history to this
    # ncatted -O -a history,global,o,c,"Data received from Mohamed Ahmed (Nelson MiP); data extracted for basin by Juliane Mai (UWaterloo);" ${outfile_prec}
    # ncatted -O -a history,global,o,c,"Data received from Mohamed Ahmed (Nelson MiP); data extracted for basin by Juliane Mai (UWaterloo);" ${outfile_temp}



    # MAKE DAILY

    # 6a- if hourly data: get time shift

    # 6b- if hourly data: shift time

    # 6c- if hourly data: save hourly data

    # 7- aggregate to daily

    # 8- save daily data
