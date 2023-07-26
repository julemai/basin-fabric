#!/usr/bin/env python
from __future__ import print_function

#
# License
# -------
# This file is part of the Basin Fabric which contains scripts to
# process data for basins, deriving attributes, processing forcings,
# and setting up and training data-driven models.

# The Basin Fabric code is free software: you can redistribute it
# and/or modify it under the terms of the MIT License.

# The Basin Fabric code library is distributed in the hope that it will
# be useful,but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
# License for more details.

# You should have received a copy of the MIT License along with the
# Basin Fabric code. If not, see
# <https://github.com/julemai/basin-fabric/blob/main/LICENSE>.

# Copyright 2023 Juliane Mai - juliane.mai@uwaterloo.ca


from pathlib import Path
import sqlite3
import datetime
import numpy as np
import netCDF4 as nc
import time

__all__ = ['write_streamflow_csv', 'write_streamflow_nc']


def write_streamflow_csv(data_dict=None,basename='streamflow_',write_symbol=False,nodata=None,period=None,station=None,silent=True):

    """
        Writes streamflow data to a CSV.


        Definition
        ----------
        def write_streamflow_csv(data_dict=None,basename='streamflow_',write_symbol=False,nodata=None,period=None,station=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        data_dict       dict            Data dictionary as returned by read_streamflow():
                                        data = { <station_id_1>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 <station_id_2>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 ... }
                                        Default: None

        basename        string          Basename of file created containing data. Basename
                                        will be appended by station ID and file ending resulting
                                        in, for example, 'streamflow_02AB001.csv'.
                                        Default: 'streamflow_'

        write_symbol    Boolean         True if data flag (called 'sym' in HYDAT) shall be written
                                        to file as additional column.
                                        Default: False

        nodata          float or        Value to fill in in case data value is 'None' in HYDAT or
                        int or          date is missing entirely in HYDAT.
                        string          Default: None

        period          dict            Dictionary specifying start and end date of data to be written
                                        to file in case they shall be cropped.
                                        Example: {'start':'1981-01-01', 'end':'2010-12-31'}.
                                        If not specified all data available will be written to file.
                                        Gaps are filled in with the NODATA value in case 'nodata' is
                                        specified.
                                        Default: None

        station         string          Station ID to write CSV for. If not specified (None) all
                                        available stations will be written into one CSV file each.
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        filenames       dict            Dictionary of names of files that are written.
                                        filenames = { station_1 : file_1,
                                                      station_2 : file_2, ... }


        Description
        -----------
        Writes streamflow data to a file. The data can be cropped to a time period specifying 'period'; the
        default is that all available data will be written. Missing data can be filled in by specifying a
        float as 'nodata' or skipped by setting 'nodata' to None (default).


        Restrictions
        ------------
        If first available date is past the 'start' date specified in 'period' or the last available date is
        prior to 'end' date specified in 'period' those "missing" dates will not be filled.


        Examples
        --------

        Read data from HYDAT

        >>> from b2_read_streamflow import read_streamflow
        >>> source    = 'hydat'
        >>> filename  = '../../data/observations/streamflow/Hydat.sqlite3'
        >>> station   = '02GA018'
        >>> pairsfile = None
        >>> data_streamflow = read_streamflow(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

        Write data from HYDAT

        >>> basename     = 'daily_discharge_'
        >>> write_symbol = False
        >>> nodata       = 9999.
        >>> station      = '02GA018'
        >>> period       = {'start':'1981-03-24','end':'2018-08-29'}
        >>> filenames_streamflow = write_streamflow_csv(data_dict=data_streamflow,basename=basename,write_symbol=write_symbol,nodata=nodata,station=station,period=period,silent=True)
        >>> print("filenames_streamflow = {}".format(filenames_streamflow))
        filenames_streamflow = {'02GA018': 'daily_discharge_02GA018.csv'}



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
        Written,  Juliane Mai, November 2022
    """

    # initialize return
    filenames = {}

    # checking inputs
    if data_dict is None:
        raise ValueError("write_streamflow_csv: dictionary containing data (data_dict) needs to be specified.")

    # if a single station is given, write only that one; otherwise write all that are given in data dictionary
    if not(station is None):
        stations = [station]
    else:
        stations = data_dict.keys()

    # loop over all stations and write data to file
    for istation in stations:

        # create file
        outfile = basename+istation+'.csv'
        ff = open(str(Path(outfile)), "w")
        filenames[istation] = outfile

        # write header
        if write_symbol:
            ff.write("date_YYYY-MM-DD,Q_m3/s,flag \n")
            flags = np.array([ data_dict[istation][ii]['sym'] for ii in data_dict[istation].keys() ])
        else:
            ff.write("date_YYYY-MM-DD,Q_m3/s \n")

        # collect data into lists
        dates = np.array([ ii for ii in data_dict[istation].keys() ])
        data  = np.array([ data_dict[istation][ii]['val'] for ii in data_dict[istation].keys() ])

        # make sure data are sorted according to dates
        idx = np.argsort(dates)
        dates = dates[idx]
        data  = data[idx]
        if write_symbol: flags = flags[idx]

        # write data
        if not(period is None):
            start_date = datetime.datetime(int(period['start'][0:4]),int(period['start'][5:7]),int(period['start'][8:10]),0,0)
            end_date   = datetime.datetime(int(period['end'  ][0:4]),int(period['end'  ][5:7]),int(period['end'  ][8:10]),0,0)

        for iidata,idata in enumerate(dates):

            curr_date = datetime.datetime(int(dates[iidata  ][0:4]),int(dates[iidata  ][5:7]),int(dates[iidata  ][8:10]),0,0)
            if not(period is None):
                if (curr_date < start_date) or (curr_date > end_date):
                    # skip this date
                    continue

            if nodata is None:
                # if no NODATA value is given, lines where data=None will be skipped (no "else")
                if not(data[iidata] is None):
                    if write_symbol:
                        ff.write(dates[iidata]+","+str(data[iidata])+","+flags[iidata]+" \n")
                    else:
                        ff.write(dates[iidata]+","+str(data[iidata])+" \n")
            else:
                # dates missing (i.e., gap to previous date) --> fill with NODATA
                if iidata > 0:
                    prev_date = datetime.datetime(int(dates[iidata-1][0:4]),int(dates[iidata-1][5:7]),int(dates[iidata-1][8:10]),0,0)
                    if not(period is None):
                        if prev_date < start_date:
                            prev_date = start_date-datetime.timedelta(days=1)
                    tdelta = (curr_date-prev_date).days
                    if tdelta > 1:
                        for itdelta in range(1,tdelta):
                            fill_date = prev_date + datetime.timedelta(days=itdelta)
                            fill_date = fill_date.strftime('%Y-%m-%d')
                            if write_symbol:
                                ff.write(fill_date+","+str(nodata)+","+flags[iidata]+" \n")
                            else:
                                ff.write(fill_date+","+str(nodata)+" \n")


                # if NODATA vlaue is given, line where data=None will be filled in with NODATA value
                if not(data[iidata] is None):
                    if write_symbol:
                        ff.write(dates[iidata]+","+str(data[iidata])+","+flags[iidata]+" \n")
                    else:
                        ff.write(dates[iidata]+","+str(data[iidata])+" \n")
                else:
                    if write_symbol:
                        ff.write(dates[iidata]+","+str(nodata)+","+flags[iidata]+" \n")
                    else:
                        ff.write(dates[iidata]+","+str(nodata)+" \n")



        # close the file
        ff.close()

        if not(silent): print("Wrote streamflow file: {}".format(outfile))

    # return list of names of files created
    return filenames


def write_streamflow_nc(info_dict=None,data_dict=None,filename='streamflow.nc',write_symbol=False,nodata=np.nan,period=None,station=None,silent=True):

    """
        Writes streamflow data to a NetCDF. All data of dictionary will be written to the same NetCDF.


        Definition
        ----------
        def write_streamflow_nc(info_dict=None,data_dict=None,filename='streamflow.nc',write_symbol=False,nodata=None,period=None,station=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        info_dict       dict            Info dictionary as returned by get_info_station():
                                        info = { <station_id_1>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 <station_id_2>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 ... }
                                        Default: None

        data_dict       dict            Data dictionary as returned by read_streamflow():
                                        data = { <station_id_1>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 <station_id_2>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 ... }
                                        Default: None

        filename        string          Name of NetCDF file created containing data. All data will be
                                        written to the same NetCDF file.
                                        Default: 'streamflow.nc'

        write_symbol    Boolean         True if data flag (called 'sym' in HYDAT) shall be written
                                        to file as additional column.
                                        Default: False

        nodata          float or        Value to fill in in case data value is 'None' in HYDAT or
                        int or          date is missing entirely.
                        string          Default: np.nan

        period          dict            Dictionary specifying start and end date of data to be written
                                        to file in case they shall be cropped.
                                        Example: {'start':'1981-01-01', 'end':'2010-12-31'}.
                                        If not specified all data available will be written to file.
                                        Gaps are filled in with the NODATA value in case 'nodata' is
                                        specified.
                                        Default: None

        station         string          Station ID to write NetCDF for. If not specified (None) all
                                        available stations will be written to the same NetCDF file.
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        filenames       dict            Dictionary of names of files that are written.
                                        filenames = { station_1 : file_1,
                                                      station_2 : file_2, ... }


        Description
        -----------
        Writes streamflow data to a file. The data can be cropped to a time period specifying 'period'; the
        default is that all available data will be written. Missing data can be filled in by specifying a
        float as 'nodata'. Default 'nodata' value is np.nan as needed by NeuralHydrology.


        Restrictions
        ------------
        If first available date is past the 'start' date specified in 'period' or the last available date is
        prior to 'end' date specified in 'period' those "missing" dates will not be filled.


        Examples
        --------

        Read information from USGS

        >>> from b2_read_streamflow import get_info_station
        >>> source    = 'usgs'
        >>> filename  = None
        >>> station   = '04069500,04084500,04085200,04087000,04096015'
        >>> pairsfile = None
        >>> info_streamflow = get_info_station(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

        Read data from USGS

        >>> from b2_read_streamflow import read_streamflow
        >>> source    = 'usgs'
        >>> filename  = None
        >>> station   = '04069500,04084500,04085200,04087000,04096015'
        >>> pairsfile = None
        >>> data_streamflow = read_streamflow(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

        Write data from USGS

        >>> filename     = 'daily_discharge.nc'
        >>> write_symbol = False
        >>> nodata       = 9999.
        >>> station      = '02GA018'
        >>> period       = {'start':'1990-03-24','end':'2018-12-31'}  # 04096015 starts 1995-07-01 ; 04084500 ends 2013-09-29
        >>> filenames_streamflow = write_streamflow_nc(info_dict=info_streamflow,data_dict=data_streamflow,filename=filename,write_symbol=write_symbol,nodata=nodata,station=station,period=period,silent=True)
        >>> print("filenames_streamflow = {}".format(filenames_streamflow))
        filenames_streamflow = {'all': 'daily_discharge.nc'}



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
        Written,  Juliane Mai, July 2023
    """

    # initialize return
    filenames = {}

    # checking inputs
    if info_dict is None:
        raise ValueError("write_streamflow_nc: dictionary containing station info (info_dict) needs to be specified.")
    if data_dict is None:
        raise ValueError("write_streamflow_nc: dictionary containing data (data_dict) needs to be specified.")

    # if a single station is given, write only that one; otherwise write all that are given in data dictionary
    if not(station is None):
        if ',' in station:
            stations = station.split(',')
        else:
            stations = [station]
    else:
        stations = data_dict.keys()

    nstations = len(stations)

    if not(period is None):
        startdate = period['start']
        enddate   = period['end']
    else:
        startdate = min([ min(data_dict[station].keys()) for station in stations ])
        enddate   = max([ max(data_dict[station].keys()) for station in stations ])
    reference_date = startdate
    ntime = (datetime.datetime.strptime(enddate, '%Y-%m-%d')-datetime.datetime.strptime(startdate, '%Y-%m-%d')).days + 1

    # gather data
    T_data    = [ itime for itime in range(ntime) ]
    lat_data  = [ info_dict[station]['lat']      for station in stations ]
    lon_data  = [ info_dict[station]['lon']      for station in stations ]
    name_data = [ info_dict[station]['name']     for station in stations ]
    area_data = [ info_dict[station]['area_km2'] for station in stations ]


    data_val = np.full((nstations,ntime),np.nan)
    data_sym = np.full((nstations,ntime),"")
    for istation,station in enumerate(stations):

        for idate in data_dict[station].keys():
            if (idate >= startdate) and (idate <= enddate):
                deltat = int((datetime.datetime.strptime(idate, '%Y-%m-%d')-datetime.datetime.strptime(startdate, '%Y-%m-%d')).days)
                if not(data_dict[station][idate]['val'] is None):
                    data_val[istation,deltat] = float(data_dict[station][idate]['val'])
                    data_sym[istation,deltat] = data_dict[station][idate]['sym']

    # open netcdf file and add some general information
    print("Write '"+filename+"' ...")
    ncid = nc.Dataset( filename, 'w') #, 'NETCDF4' )

    # Global Attributes
    ncid.Conventions = 'CF-1.6'
    ncid.License     = 'The data were downloaded from WSC (Canada) and USGS (USA) and are under the same licence the data are there.'
    ncid.history     = 'Created ' + time.ctime(time.time()) + ' Juliane Mai.'
    ncid.source      = 'Written by CaSPAr test script (https://github.com/kckornelsen/CaSPAR_Public).'
    ncid.featureType = 'timeSeries'
    ncid.description = 'Gauging station file created using Basin Fabric (https://github.com/julemai/basin-fabric).'

    # Dimensions
    dimid_X = ncid.createDimension('nstations',nstations)
    dimid_T = ncid.createDimension('time',) # UNLIMITED

    # --------------------------
    # Define the dimension for the string length
    string_length = 100

    # Define the dimension and variable for the strings array
    ncid.createDimension('string_length', string_length)

    # --------------------------
    # Variables: station ID
    id_varid = ncid.createVariable('station_id','S1', ('nstations', 'string_length'),zlib=True)
    #id_varid = ncid.createVariable('station_id',str, ('nstations',),zlib=True)

    # Attributes: name
    id_varid.long_name      = 'Gauge station ID'
    id_varid.cf_role        = 'timeseries_id'

    # Convert the array of strings to a fixed-size numpy array
    stations_fixed_size = np.zeros((nstations, string_length), dtype='S1')
    for ii, string in enumerate(stations):
        stations_fixed_size[ii,:len(string)] = np.array(list(string), dtype='S1')

    # Write data: name
    id_varid[:] = stations_fixed_size #stations
    #id_varid[:] = stations

    # --------------------------
    # Variables: streamflow
    streamflow_varid = ncid.createVariable('Q','f4',('nstations','time',),zlib=True)

    # Attributes: lat/lon
    streamflow_varid.long_name      = 'discharge'
    streamflow_varid.units          = 'm**3 s**-1'
    streamflow_varid.coordinates    = 'station_id'

    # Write data: lat/lon
    streamflow_varid[:] = data_val

    # --------------------------
    # Variables: time
    time_varid = ncid.createVariable('time','i4',('time',),zlib=True)

    # Attributes: time
    time_varid.long_name     = 'time'
    time_varid.units         = 'days since ' + reference_date + ' 00:00:00'
    time_varid.calendar      = 'gregorian'
    time_varid.standard_name = 'time'
    time_varid.axis          = 'T'

    # Write data: time
    time_varid[:] = T_data

    # --------------------------
    # Variables: lat/lon
    lat_varid = ncid.createVariable('lat','f4',('nstations'),zlib=True)
    lon_varid = ncid.createVariable('lon','f4',('nstations'),zlib=True)

    # Attributes: lat/lon
    lat_varid.long_name      = 'latitude'
    lon_varid.long_name      = 'longitude'
    lat_varid.units          = 'degrees_north'
    lon_varid.units          = 'degrees_east'
    lat_varid.standard_name  = 'latitude'
    lon_varid.standard_name  = 'longitude'

    # Write data: lat/lon
    lat_varid[:] = lat_data
    lon_varid[:] = lon_data

    # --------------------------
    # Variables: name
    name_varid = ncid.createVariable('station_info', 'S1', ('nstations', 'string_length'),zlib=True)

    # Attributes: name
    name_varid.long_name      = 'Name of gauge station'
    name_varid.units          = '1'

    # Convert the array of strings to a fixed-size numpy array
    name_data_fixed_size = np.zeros((nstations, string_length), dtype='S1')
    print(name_data)
    for ii, string in enumerate(name_data):
        string = string.replace('\xc8','E').replace('\xc9','E').replace('\xc0','A').replace('\xc1','A')
        name_data_fixed_size[ii,:len(string)] = np.array(list(string), dtype='S1')

    # Write data: name
    name_varid[:] = name_data_fixed_size  # name_data




    ncid.close()






    if not(silent): print("Wrote streamflow file: {}".format(filename))

    # set return
    filenames = { 'all': filename }

    # return list of names of files created
    return filenames



if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    # from b2_read_streamflow import get_info_station

    # source    = 'hydat'
    # filename = "../../data/observations/streamflow/Hydat.sqlite3"
    # pairsfile = None
    # station   = '02GA018'
    # # pairsfile = '../data/Q_C_pairs.csv'
    # # station   = None
    # data_info = get_info_station(source=source,filename=filename,station=station,pairsfile=None,silent=True)

    # filenames_info = write_info_csv(data_dict=data_info,basename='information_',station=station,silent=False)



    # from b2_read_streamflow import read_streamflow

    # source    = 'hydat'
    # filename = "../../data/observations/streamflow/Hydat.sqlite3"
    # pairsfile = None
    # station   = '02GA018'
    # # pairsfile = '../data/Q_C_pairs.csv'
    # # station   = None
    # data_streamflow = read_streamflow(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

    # basename     = 'daily_discharge_'  # results in 'daily_discharge_<station-id>.csv'
    # write_symbol = False                         # quality marker 'symbol' as given by HYDAT won't be written to file
    # nodata       = 9999.
    # station      = '02GA018'
    # period       = {'start':'1981-03-24','end':'2018-08-29'}
    # filenames_streamflow = write_streamflow_csv(data_dict=data_streamflow,basename=basename,write_symbol=write_symbol,nodata=nodata,station=station,period=period,silent=False)


    # from b2_read_streamflow import get_info_station
    # source    = 'usgs'
    # filename  = None
    # station   = '04069500,04084500,04085200,04087000,04096015'
    # pairsfile = None
    # info_streamflow = get_info_station(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

    # from b2_read_streamflow import read_streamflow
    # source    = 'usgs'
    # filename  = None
    # station   = '04069500,04084500,04085200,04087000,04096015'
    # pairsfile = None
    # data_streamflow = read_streamflow(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)

    # filename     = 'daily_discharge.nc'
    # write_symbol = False
    # nodata       = np.nan
    # station      =  '04069500,04084500,04085200,04087000,04096015'
    # period       = {'start':'1990-03-24','end':'2018-12-31'}  # 04096015 starts 1995-07-01 ; 04084500 ends 2013-09-29
    # filenames_streamflow = write_streamflow_nc(info_dict=info_streamflow,data_dict=data_streamflow,filename=filename,write_symbol=write_symbol,nodata=nodata,station=station,period=period,silent=True)
    # print("filenames_streamflow = {}".format(filenames_streamflow))
