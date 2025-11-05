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
import pandas as pd
import requests
import json

__all__ = ['get_info_station', 'get_info_tables', 'get_info_columns', 'read_streamflow', 'get_periods', 'filter_streamflow']

def get_info_station(source=None,filename='/tmp/test',station=None,pairsfile=None,silent=True):
    """
        Reads STREAMFLOW data file and returns information for given station, i.e.,
        lat/lon, drainage area (from table STATIONS) and time period daily STREAMFLOW is available.

        Definition
        ----------
        def get_info_station(source=None,filename='/tmp/test',station=None,pairsfile=None,silent=False):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to STREAMFLOW data were retrieved from.
                                        Currently implemented:
                                        hydat ... sqlite3 database retrieved from
                                                  http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/
                                        usgs  ... data requested from USGS for US stations using
                                                  "curl https://waterservices.usgs.gov/nwis/dv/?format=json\
                                                   \&sites=<site-id>\
                                                   \&startDT=<YYYY-MM-DD>\
                                                   \&parameterCd=00060
                                                   \&endDT=<YYYY-MM-DD>
                                                   \&siteStatus=all"
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        station         string          Station ID to read and obtain unique list of available variables from.
                                        Either station or pairsfile needs to be specified. Multiple stations
                                        can be specified like "station1,station2,station3".
                                        Default: None

        pairsfile       string          Name of file containing pairs of streamflow and concentration stations.
                                        Format:
                                        ----> C station ID,Q station ID,Name,LAT,LONG,Area(km2)
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        info            dict            Dictionary with unique sets of avaialable variables and time period
                                        data are available for.
                                        info = { 'lat'      : <latitude>,
                                                 'lon'      : <longitude>,
                                                 'area_km2' : <drainage_area_in_km2>
                                                 'name'     : <station name without commas>
                                                 'Q'        : {start: YYYY-MM-DD, end: YYYY-MM-DD}
                                               }

        Description
        -----------
        Reads data of a station (or list of stations) for one specific variable from a STREAMFLOW dataset.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read information from HYDAT

        >>> source   = 'hydat'
        >>> filename = '../../data/observations/streamflow/Hydat.sqlite3'
        >>> station  = '02GA018'
        >>> info = get_info_station(source=source,filename=filename,station=station,silent=True)
        >>> print('info = {}'.format(info))
        info = {'02GA018': {'name': 'NITH RIVER AT NEW HAMBURG', 'lat': 43.377220153808594, 'lon': -80.71080780029297, 'area_km2': 544.0, 'Q': {'start': '1950-04-01', 'end': '2020-12-31'}}}

        Read infomration from USGS
        >>> source   = 'usgs'
        >>> filename = None
        >>> station  = '04069500'
        >>> info = get_info_station(source=source,filename=filename,station=station,silent=True)
        >>> print('info = {}'.format(info))
        info = {'02GA018': {'name': 'NITH RIVER AT NEW HAMBURG', 'lat': 43.377220153808594, 'lon': -80.71080780029297, 'area_km2': 544.0, 'Q': {'start': '1950-04-01', 'end': '2020-12-31'}}}


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
        Written,  Juliane Mai, December 2022
    """

    # checking inputs
    if source is None:
        raise ValueError("get_info_station: source needs to be specified")

    if (station is None) and (pairsfile is None):
        raise ValueError("get_info_station: either station or pairsfile needs to be specified")
    elif not(station is None) and not(pairsfile is None):
        raise ValueError("get_info_station: either station or pairsfile needs to be specified. not both.")
    elif not(station is None):
        if ',' in station:
            stations = station.split(',')
        else:
            stations = [ station ]
    elif not(pairsfile is None):
        # open file and read content
        ff = open(str(Path(pairsfile)), "r")
        lines = ff.readlines()
        ff.close()

        stations = []
        for ll in lines[1:]:
            stations.append(ll.strip().split(',')[1])  # Q stations

    else:
        raise ValueError("get_info_station: Not sure what happened!")

    # make sure source is implemented
    sources = ['hydat', 'usgs']
    if not(source in sources):
        raise ValueError('get_info_station: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'hydat':

        # create a SQL connection to our SQLite database
        con = sqlite3.connect(filename)

        # define query (basically all data; except (monthly) MIN and MAX)
        cur = con.cursor()

        # get dates --> for period available
        query='''SELECT F.STATION_NUMBER,YEAR,MONTH
                FROM DLY_FLOWS F
                INNER JOIN STATIONS S
                ON F.STATION_NUMBER = S.STATION_NUMBER
        '''

        # retrieve all data
        data_all_time = []
        for row in cur.execute(query):
            data_all_time.append(row)
        data_all_time = np.array([ list(dd) for dd in data_all_time ])

        # get dates --> for period available
        query='''SELECT STATION_NUMBER,STATION_NAME,LATITUDE,LONGITUDE,DRAINAGE_AREA_GROSS
                FROM STATIONS
        '''

        # retrieve all data
        data_all_latlon = []
        for row in cur.execute(query):
            data_all_latlon.append(row)

        # close connection
        con.close()

        data = {}
        for idata_all in data_all_latlon:

            station = idata_all[0]
            if station in stations:

                # find period where data are available
                idx = np.where(data_all_time[:,0] == station )[0]
                tt = data_all_time[idx]
                tt = np.sort([ '{:04d}-{:02d}'.format(int(itt[1]),int(itt[2])) for itt in tt ])
                tt_min = tt[0]+'-01'  # first day of first month
                year  = int(tt[-1].split('-')[0])
                month = int(tt[-1].split('-')[1])
                if month < 12:
                    length_month = (datetime.date(year, month+1, 1) - datetime.date(year, month, 1)).days
                else:
                    length_month = 31
                tt_max = "{:04d}-{:02d}-{:02d}".format(year,month,length_month)  # last day of last month

                tmp = {}
                tmp['name']     = idata_all[1].replace(',',';')
                tmp['lat']      = idata_all[2]
                tmp['lon']      = idata_all[3]
                tmp['area_km2'] = idata_all[4]
                tmp['Q']        = {'start': tt_min , 'end': tt_max }

                if station in data.keys():
                    data[station].update( tmp )
                else:
                    data[station] = tmp

                if not(silent): print("info of station {}: {}".format(station,data[station]))

    elif source == 'usgs':

        data = {}
        for station in stations:

            start_period = '1880-01-01'  # can be a lot of data...

            # more info about curl commands:
            # - https://help.waterdata.usgs.gov/faq/automated-retrievals
            # - https://waterservices.usgs.gov/rest/Site-Service.html

            # get most data
            api_str = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites='+station+'&parameterCd=00060&statCd=00003&siteStatus=all&startDT='+start_period  #+'&endDT=2023-03-20'
            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

            if not(silent): print("   Downloading:        {}".format(api_str))
            response1 = requests.get(api_str, headers=headers)

            # get drainage area
            api_str = 'https://waterservices.usgs.gov/nwis/site/?format=rdb&sites='+station+'&siteOutput=expanded'
            headers = {'Accept-Charset': 'UTF-8'}

            if not(silent): print("   Downloading:        {}".format(api_str))
            response2 = requests.get(api_str, headers=headers)

            if check_status_usgs(response1.status_code):

                # load data
                usgs = json.loads(response1.content.decode('utf-8'))
                json_dump = json.dumps(usgs)

                # print("usgs = ",usgs)
                # print("keys = ",usgs.keys())
                # print("more = ",usgs['value']['timeSeries'][0]['variable']['unit'].keys())

                if len(usgs['value']['timeSeries']) > 0:

                    tmp = {}
                    tmp['name']     = usgs['value']['timeSeries'][0]['sourceInfo']['siteName'].replace(',',';')
                    tmp['lat']      = usgs['value']['timeSeries'][0]['sourceInfo']['geoLocation']['geogLocation']['latitude']
                    tmp['lon']      = usgs['value']['timeSeries'][0]['sourceInfo']['geoLocation']['geogLocation']['longitude']
                    tmp['area_km2'] = None
                    tmp['unit']     = usgs['value']['timeSeries'][0]['variable']['unit']['unitCode']
                    if 'noDataValue' in usgs['value']['timeSeries'][0]['variable']['unit'].keys():
                        tmp['nodata'] = usgs['value']['timeSeries'][0]['variable']['unit']['noDataValue']
                    else:
                        tmp['nodata'] = None

                    # find date range
                    print()
                    dates = usgs['value']['timeSeries'][0]['values'][0]['value']               # [ {'value': '787', 'qualifiers': ['A'], 'dateTime': '1956-02-24T00:00:00.000'},
                    #                                                                          #   {'value': '765', 'qualifiers': ['A'], 'dateTime': '1956-02-25T00:00:00.000'}, ...]
                    dates = np.array([ idate['dateTime'].split('T')[0] for idate in dates ])   # '1956-02-24T00:00:00.000' --> '1956-02-24
                    tt_min = min(dates)
                    tt_max = max(dates)
                    tmp['Q']        = {'start': tt_min , 'end': tt_max }

                    if check_status_usgs(response2.status_code):

                        usgs = response2.content.decode('utf-8').split('\n')

                        # remove commented and blank lines
                        usgs_tmp = []
                        for ll in usgs:
                            if not( ll.strip().startswith('#') or len(ll.strip()) == 0):
                                usgs_tmp.append(ll)
                        usgs = usgs_tmp

                        # split columns
                        usgs = [ ll.split('\t') for ll in usgs ]

                        # # FOR DEBUGGING
                        # if not(silent):
                        #     nattr = len(usgs[0])
                        #     for iattr,attr in enumerate(usgs[0]):
                        #         print('   >>> {} = {}'.format(attr,usgs[2][iattr]))

                        # find index of contributing drainage area
                        try:
                            idx = usgs[0].index('drain_area_va')
                        except:
                            raise ValueError('   "drain_area_va" not found in list of attributes: {}'.format(usgs[0]))

                        # set area (given in mi**2)
                        if usgs[2][idx] != '':
                            tmp['area_km2'] = float(usgs[2][idx]) * 1.609344**2
                        else:
                            print("   Area for station {} not found. Set to nan.".format(station))
                            tmp['area_km2'] = np.nan

                    # add station info to list
                    if station in data.keys():
                        data[station].update( tmp )
                    else:
                        data[station] = tmp

                    if not(silent): print("info of station {}: {}".format(station,data[station]))

                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>")
                    print("WARNING: No data found for station {}.".format(station))
                    print(">>>>>>>>>>>>>>>>>>>>>>>>")

    else:
        raise ValueError('get_info_station: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    return data


def check_status_usgs(status_code):

    # checks response status when data are requested from USGS
    # codes described here: https://waterservices.usgs.gov/rest/Site-Service.html#Error

    if (status_code == 304):
        raise ValueError('request_concentration: status_code=304: Not_Modified. This indicates your request was redirected using the proper URL. This may occur if the "path" of your URL is not fully qualified. Ideally a / is placed before the ? in the URL. Adding in this slash may make this go away. However, the request should still be processed. If this becomes annoying, you may also be able to tell your client program to automatically follow redirects.')
    elif (status_code == 400):
        raise ValueError('request_concentration: status_code=400: Bad_Request. This often occurs if the URL arguments are inconsistent. An accompanying error should describe why the request was bad. Reasons include: (a) Using startDT and endDT with the period argument. (b) Mixing startDt and endDt arguments where startDt includes a time zone and endDt does not.')
    elif (status_code == 403):
        raise ValueError('request_concentration: status_code=403: Access_Forbidden. This should only occur if for some reason the USGS has blocked your Internet Protocol (IP) address from using the service. This can happen if we believe that your use of the service is so excessive that it is seriously impacting others using the service. To get unblocked, send us the URL you are using along with your clients IP using this form. We may require changes to your query and frequency of use in order to give you access to the service again.')
    elif (status_code == 404):
        raise ValueError('request_concentration: status_code=404: Not_Found. Returned if and only if the query expresses a combination of elements where data do not exist. For multi-site queries, if any data are found, it is returned for those site/parameters/date ranges where there are data. Conditions that would return a 404 Not Found include: (a) The site number(s) are invalid. (b) The site number(s) are valid but the requested parameter(s) are not served for these sites. (c) No values exist for the requested date range. For example, a gage might be down for a period of time due to storm damage when it would normally have data.')
    elif (status_code == 500):
        raise ValueError('request_concentration: status_code=500: Internal_Server_Error. If you see this, it means there is a problem with the web service itself. It usually means the application server is down unexpectedly. This could be caused by a host of conditions but changing your query will not solve this problem. The application support team has to fix it. Most of these errors are quickly detected and the support team is notified if they occur.')
    elif (status_code == 503):
        raise ValueError('request_concentration: status_code=503: Service_Unavailable.The server is currently unable to handle the request due to a temporary overloading or maintenance of the server. The implication is that this is a temporary condition which will be alleviated after some delay.')
    elif (status_code == 200):
        return( True )
    else:

        raise ValueError('request_concentration: status_code={}: Please contact the DataStream team'.format(status_code))


def get_info_tables(source=None,filename='/tmp/test',silent=True):
    """
        Reads streamflow data (usually Hydat) and returns list of available tables.


        Definition
        ----------
        def get_info_tables(source=None,filename='/tmp/test',silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to STREAMFLOW data were retrieved from.
                                        Currently implemented:
                                        hydat ... data retrieved from
                                                  http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        tables          list            List of tables available in database:
                                        tables = [ table_1, table_2, ... ]


        Description
        -----------
        Reads database and returns list of available tables. Usually the table for
        daily streamflow would be read but some pther tables might be of interest
        as well. This helper function shall facilitate exploring the entire database.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read information from HYDAT

        >>> source   = 'hydat'
        >>> filename = '../../data/observations/streamflow/Hydat.sqlite3'
        >>> tables_streamflow = get_info_tables(source=source,filename=filename,silent=True)
        >>> print('tables_streamflow = {}'.format(tables_streamflow))
        tables_streamflow = ['STATIONS', 'CONCENTRATION_SYMBOLS', 'SED_SAMPLES_PSD', 'ANNUAL_INSTANT_PEAKS', 'STN_DATUM_UNRELATED', 'DATA_SYMBOLS', 'SED_VERTICAL_LOCATION', 'STN_DATA_COLLECTION', 'PEAK_CODES', 'SED_DATA_TYPES', 'MEASUREMENT_CODES', 'SED_VERTICAL_SYMBOLS', 'DATA_TYPES', 'DLY_FLOWS', 'STN_REMARKS', 'STN_DATUM_CONVERSION', 'AGENCY_LIST', 'SED_DLY_SUSCON', 'STN_OPERATION_SCHEDULE', 'STN_DATA_RANGE', 'PRECISION_CODES', 'SED_DLY_LOADS', 'DLY_LEVELS', 'OPERATION_CODES', 'STN_REGULATION', 'DATUM_LIST', 'ANNUAL_STATISTICS', 'VERSION', 'REGIONAL_OFFICE_LIST', 'SAMPLE_REMARK_CODES', 'STN_REMARK_CODES', 'SED_SAMPLES', 'STN_STATUS_CODES']


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
        Written,  Juliane Mai, December 2022
    """

    # checking inputs
    if source is None:
        raise ValueError("get_info_tables: source needs to be specified")

    # make sure source is implemented
    sources = ['hydat']
    if not(source in sources):
        raise ValueError('get_info_tables: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'hydat':

        # create a SQL connection to our SQLite database
        con = sqlite3.connect(filename)

        # define query (basically all data; except (monthly) MIN and MAX)
        cur = con.cursor()

        # list all available tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        tables = [ tt[0] for tt in tables ]
        if not(silent): print("tables: {}".format(tables))

        # close connection
        con.close()

    else:
        raise ValueError("get_info_tables: source needs to be one of the following: {}".format(sources))

    return tables


def get_info_columns(source=None,filename='/tmp/test',table=None,silent=True):
    """
        Reads streamflow data (usually Hydat) and returns list of available columns of specified table.


        Definition
        ----------
        def get_info_columns(source=None,filename='/tmp/test',table=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to STREAMFLOW data were retrieved from.
                                        Currently implemented:
                                        hydat ... data retrieved from
                                                  http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        table           string          Name of table columns are requested for
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        columns         list            List of columns in specified table of database:
                                        columns = [ column_1, column_2, ... ]


        Description
        -----------
        Reads database and returns list of available columns in the specified table.
        If the table names are not known yet, one can run get_info_tables() to retrieve
        a list of available tables. Usually the table for daily streamflow ('DLY_FLOWS')
        would be read but some pther tables might be of interest as well. This helper
        function shall facilitate exploring the entire database.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read information from HYDAT

        >>> source   = 'hydat'
        >>> filename = '../../data/observations/streamflow/Hydat.sqlite3'
        >>> columns_streamflow = get_info_columns(source=source,filename=filename,table='DLY_FLOWS',silent=True)
        >>> print("columns_streamflow = {}".format(columns_streamflow))
        columns_streamflow = ['STATION_NUMBER', 'YEAR', 'MONTH', 'FULL_MONTH', 'NO_DAYS', 'MONTHLY_MEAN', 'MONTHLY_TOTAL', 'FIRST_DAY_MIN', 'MIN', 'FIRST_DAY_MAX', 'MAX', 'FLOW1', 'FLOW_SYMBOL1', 'FLOW2', 'FLOW_SYMBOL2', 'FLOW3', 'FLOW_SYMBOL3', 'FLOW4', 'FLOW_SYMBOL4', 'FLOW5', 'FLOW_SYMBOL5', 'FLOW6', 'FLOW_SYMBOL6', 'FLOW7', 'FLOW_SYMBOL7', 'FLOW8', 'FLOW_SYMBOL8', 'FLOW9', 'FLOW_SYMBOL9', 'FLOW10', 'FLOW_SYMBOL10', 'FLOW11', 'FLOW_SYMBOL11', 'FLOW12', 'FLOW_SYMBOL12', 'FLOW13', 'FLOW_SYMBOL13', 'FLOW14', 'FLOW_SYMBOL14', 'FLOW15', 'FLOW_SYMBOL15', 'FLOW16', 'FLOW_SYMBOL16', 'FLOW17', 'FLOW_SYMBOL17', 'FLOW18', 'FLOW_SYMBOL18', 'FLOW19', 'FLOW_SYMBOL19', 'FLOW20', 'FLOW_SYMBOL20', 'FLOW21', 'FLOW_SYMBOL21', 'FLOW22', 'FLOW_SYMBOL22', 'FLOW23', 'FLOW_SYMBOL23', 'FLOW24', 'FLOW_SYMBOL24', 'FLOW25', 'FLOW_SYMBOL25', 'FLOW26', 'FLOW_SYMBOL26', 'FLOW27', 'FLOW_SYMBOL27', 'FLOW28', 'FLOW_SYMBOL28', 'FLOW29', 'FLOW_SYMBOL29', 'FLOW30', 'FLOW_SYMBOL30', 'FLOW31', 'FLOW_SYMBOL31']


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
        Written,  Juliane Mai, December 2022
    """

    # checking inputs
    if source is None:
        raise ValueError("get_info_columns: source needs to be specified")
    if table is None:
        raise ValueError("get_info_columns: source needs to be specified")

    # make sure source is implemented
    sources = ['hydat']
    if not(source in sources):
        raise ValueError('get_info_columns: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'hydat':

        # create a SQL connection to our SQLite database
        con = sqlite3.connect(filename)

        # define query (basically all data; except (monthly) MIN and MAX)
        cur = con.cursor()

        # list all available columns
        cur.execute("SELECT * FROM {}".format(table))
        columns = cur.description
        columns = [ cc[0] for cc in columns ]
        if not(silent): print("columns of table {}: {}".format(table,columns))

        # close connection
        con.close()

    else:
        raise ValueError("get_info_columns: source needs to be one of the following: {}".format(sources))

    return columns


def read_streamflow(source=None,filename='/tmp/test',station=None,pairsfile=None,silent=True):
    """
        Reads data for a specific station(s) and variable. The stations can also be provided
        as a CSV file which specifies the pairs of concentration/streamflow gauge IDs.



        Definition
        ----------
        def read_streamflow(source=None,filename='/tmp/test',station=None,variable=None,pairsfile=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to STREAMFLOW data were retrieved from.
                                        Currently implemented:
                                        hydat ... data retrieved from
                                                  http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        station         string          Station ID to read and obtain unique list of available variables from.
                                        Either station or pairsfile needs to be specified. Multiple stations
                                        can be specified like "station1,station2,station3".
                                        Default: None

        pairsfile       string          Name of file containing pairs of streamflow and concentration stations.
                                        Format:
                                        ----> C station ID,Q station ID,Name,LAT,LONG,Area(km2)
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        data            dict            Dictionary of time steps and data point:
                                        data = { <station_id_1>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 <station_id_2>: { <date_1>: <value_1>,
                                                                   <date_2>: <value_2>,
                                                                   ... },
                                                 ... }


        Description
        -----------
        Reads data of a station (or list of stations) for one specific variable from a STREAMFLOW dataset.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read data from HYDAT

        >>> source    = 'hydat'
        >>> filename  = '../../data/observations/streamflow/Hydat.sqlite3'
        >>> station   = '02GA018'
        >>> pairsfile = None
        >>> data_streamflow = read_streamflow(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)
        >>> print("data_streamflow['02GA018']['1984-11-01'] = {}".format(data_streamflow['02GA018']['1984-11-01']))
        data_streamflow['02GA018']['1984-11-01'] = {'val': 1.5499999523162842, 'sym': 'E'}
        >>> print("data_streamflow['02GA018']['1984-11-02'] = {}".format(data_streamflow['02GA018']['1984-11-02']))
        data_streamflow['02GA018']['1984-11-02'] = {'val': 1.7799999713897705, 'sym': 'E'}
        >>> print("data_streamflow['02GA018']['1984-11-03'] = {}".format(data_streamflow['02GA018']['1984-11-03']))
        data_streamflow['02GA018']['1984-11-03'] = {'val': 1.600000023841858, 'sym': 'E'}


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

    # checking inputs
    if source is None:
        raise ValueError("read_streamflow: source needs to be specified")

    if (station is None) and (pairsfile is None):
        raise ValueError("read_streamflow: either station or pairsfile needs to be specified")
    elif not(station is None) and not(pairsfile is None):
        raise ValueError("read_streamflow: either station or pairsfile needs to be specified. not both.")
    elif not(station is None):
        if ',' in station:
            stations = station.split(',')
        else:
            stations = [ station ]
    elif not(pairsfile is None):
        # open file and read content
        ff = open(str(Path(pairsfile)), "r")
        lines = ff.readlines()
        ff.close()

        stations = []
        for ll in lines[1:]:
            stations.append(ll.strip().split(',')[1])  # Q stations

    else:
        raise ValueError("read_streamflow: Not sure what happened!")

    if not(silent): print("stations: ",stations)

    # make sure source is implemented
    sources = ['hydat', 'usgs']
    if not(source in sources):
        raise ValueError('read_streamflow: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'hydat':

        # create a SQL connection to our SQLite database
        con = sqlite3.connect(filename)

        # define query (basically all data; except (monthly) MIN and MAX)
        cur = con.cursor()

        # request string
        query='''SELECT F.STATION_NUMBER,YEAR,MONTH,
                        FLOW1,FLOW_SYMBOL1,FLOW2,FLOW_SYMBOL2,FLOW3,FLOW_SYMBOL3,FLOW4,FLOW_SYMBOL4,
                        FLOW5,FLOW_SYMBOL5,FLOW6,FLOW_SYMBOL6,FLOW7,FLOW_SYMBOL7,FLOW8,FLOW_SYMBOL8,
                        FLOW9,FLOW_SYMBOL9,FLOW10,FLOW_SYMBOL10,FLOW11,FLOW_SYMBOL11,FLOW12,FLOW_SYMBOL12,
                        FLOW13,FLOW_SYMBOL13,FLOW14,FLOW_SYMBOL14,FLOW15,FLOW_SYMBOL15,FLOW16,FLOW_SYMBOL16,
                        FLOW17,FLOW_SYMBOL17,FLOW18,FLOW_SYMBOL18,FLOW19,FLOW_SYMBOL19,FLOW20,FLOW_SYMBOL20,
                        FLOW21,FLOW_SYMBOL21,FLOW22,FLOW_SYMBOL22,FLOW23,FLOW_SYMBOL23,FLOW24,FLOW_SYMBOL24,
                        FLOW25,FLOW_SYMBOL25,FLOW26,FLOW_SYMBOL26,FLOW27,FLOW_SYMBOL27,FLOW28,FLOW_SYMBOL28,
                        FLOW29,FLOW_SYMBOL29,FLOW30,FLOW_SYMBOL30,FLOW31,FLOW_SYMBOL31
                FROM DLY_FLOWS F
                INNER JOIN STATIONS S
                ON F.STATION_NUMBER = S.STATION_NUMBER
        '''

        # retrieve all data
        data_all = []
        for row in cur.execute(query):
            data_all.append(row)

        # close connection
        con.close()

        data = {}
        for idata_all in data_all:

            station = idata_all[0]
            if station in stations:

                year = idata_all[1]
                month = idata_all[2]
                if month < 12:
                    length_month = (datetime.date(year, month+1, 1) - datetime.date(year, month, 1)).days
                else:
                    length_month = 31

                tmp = {}
                for iday in range(length_month):
                    tmp['{:04d}-{:02d}-{:02d}'.format(year, month,1+iday)] = {'val':idata_all[3+iday*2],'sym':idata_all[4+iday*2]}

                if station in data.keys():
                    data[station].update( tmp )
                else:
                    data[station] = tmp

                # print(idata_all)

    elif source == 'usgs':

        data = {}
        for station in stations:

            # more info about curl commands:
            # - https://help.waterdata.usgs.gov/faq/automated-retrievals
            # - https://waterservices.usgs.gov/rest/Site-Service.html

            # get most data
            start_period = '1880-01-01'  # can be a lot of data...
            # statCd=00003 is NEW :: it is now precisely requesting "mean" streamflow.
            #                        before it requested min/max/mean and just the first one was analysed
            #                        so basically we looked at min Q all the time
            api_str = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites='+station+'&parameterCd=00060&statCd=00003&siteStatus=all&startDT='+start_period  #+'&endDT=2023-03-20'
            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

            if not(silent): print("   Downloading:        {}".format(api_str))
            response1 = requests.get(api_str, headers=headers)

            # # get drainage area
            # api_str = 'https://waterservices.usgs.gov/nwis/site/?format=rdb&sites='+station+'&siteOutput=expanded'
            # headers = {'Accept-Charset': 'UTF-8'}

            # if not(silent): print("   Downloading:        {}".format(api_str))
            # response2 = requests.get(api_str, headers=headers)

            if check_status_usgs(response1.status_code):

                # load data
                usgs = json.loads(response1.content.decode('utf-8'))
                if len(usgs['value']['timeSeries']) > 0:
                    all_data = usgs['value']['timeSeries'][0]['values'][0]['value']        # get only data
                    #                                                                      # [ {'value': '787', 'qualifiers': ['A'], 'dateTime': '1956-02-24T00:00:00.000'},
                    #                                                                      #   {'value': '765', 'qualifiers': ['A'], 'dateTime': '1956-02-25T00:00:00.000'}, ...]
                    unit = usgs['value']['timeSeries'][0]['variable']['unit']['unitCode']  # unit (for conversion of 'ft3/s' --> 'm3/s')

                    # conversion factor
                    if unit == 'ft3/s':
                        mult = 0.028316832
                        if not(silent): print("   Data for station {} will be converted from ft3/s to m3/s.".format(station))
                    else:
                        mult = 1.0

                    # gather data
                    tmp = {}
                    for idata in all_data:
                        idate = [ int(ii) for ii in idata['dateTime'].split('T')[0].split('-') ]
                        tmp['{:04d}-{:02d}-{:02d}'.format(idate[0],idate[1],idate[2])] = {'val':float(idata['value'])*mult,'sym':','.join(idata['qualifiers'])}

                    if station in data.keys():
                        data[station].update( tmp )
                    else:
                        data[station] = tmp

                    if not(silent): print("   Data of station {}: {} ... {}".format(station,dict(list(data[station].items())[0:2]),dict(list(data[station].items())[-2:])))
                    if not(silent): print("\n")

    else:
        raise ValueError("read_streamflow: source needs to be one of the following: {}".format(sources))

    return data


def get_periods(dates=None,silent=True):

    """
        Returns the periods of consecutive dates from a provided list of dates.



        Definition
        ----------
        def get_periods(dates,silent=True):


        Input           Format          Description
        -----           -----           -----------
        dates           list            List of dates in format YYYY-MM-DD.
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        periods         list(lists)     List of lists containing start and end date of each period of consecutive dates. For example,
                                        [ [2000-01-01,2000-12-31], [2001-02-01, 2001,12,31] ]
                                        if dates for January 2001 are missing.


        Description
        -----------
        Reads data of a station (or list of stations) for one specific variable from a STREAMFLOW dataset.


        Restrictions
        ------------
        Expected to be dates in format YYYY-MM-DD. Sub-daily dates are not considered.


        Examples
        --------

        Find periods

        >>> dates = ['1991-02-01', '1991-02-02', '1991-02-03', '1991-02-04', '1991-02-05', '1991-02-06', '1991-02-07']
        >>> periods = get_periods(dates=dates,silent=True)
        >>> print("periods = {}".format(periods))
        periods = [['1991-02-01', '1991-02-07']]

        >>> dates = ['1991-02-01', '1991-02-02', '1991-02-03', '1991-02-05', '1991-02-06', '1991-02-07']
        >>> periods = get_periods(dates=dates,silent=True)
        >>> print("periods = {}".format(periods))
        periods = [['1991-02-01', '1991-02-03'], ['1991-02-05', '1991-02-07']]


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
        Written,  Juliane Mai, January 2023
    """

    # initialize return
    periods = []

    # check inputs
    if dates is None:
        raise ValueError("get_periods: list of dates in format YYYY-MM-DD needs to be provided.")

    start = None
    last = None
    for idates in dates:
        if start is None:
            start = idates
            last = idates
        else:
            if datetime.datetime.strptime(idates, "%Y-%m-%d") == datetime.datetime.strptime(last, "%Y-%m-%d")+datetime.timedelta(days=1):
                last = idates
            else:
                end = last
                periods.append([start,end])
                start = idates
                last = idates
    periods.append([start,dates[-1]])

    return periods


from typing import Union

def fill_with_hard_limit(
        df_or_series: Union[pd.DataFrame, pd.Series], limit: int,
        fill_method='interpolate',
        **fill_method_kwargs) -> Union[pd.DataFrame, pd.Series]:
    """
    Implementation found:
    https://stackoverflow.com/questions/30533021/interpolate-or-extrapolate-only-small-gaps-in-pandas-dataframe
    (reply 2)

    The fill methods from Pandas such as ``interpolate`` or ``bfill``
    will fill ``limit`` number of NaNs, even if the total number of
    consecutive NaNs is larger than ``limit``. This function instead
    does not fill any data when the number of consecutive NaNs
    is > ``limit``.

    Adapted from: https://stackoverflow.com/a/30538371/11052174

    :param df_or_series: DataFrame or Series to perform interpolation
        on.
    :param limit: Maximum number of consecutive NaNs to allow. Any
        occurrences of more consecutive NaNs than ``limit`` will have no
        filling performed.
    :param fill_method: Filling method to use, e.g. 'interpolate',
        'bfill', etc.
    :param fill_method_kwargs: Keyword arguments to pass to the
        fill_method, in addition to the given limit.

    :returns: A filled version of the given df_or_series according
        to the given inputs.
    """

    # Keep things simple, ensure we have a DataFrame.
    try:
        df = df_or_series.to_frame()
    except AttributeError:
        df = df_or_series

    # Initialize our mask.
    mask = pd.DataFrame(True, index=df.index, columns=df.columns)

    # Get cumulative sums of consecutive NaNs.
    grp = (df.notnull() != df.shift().notnull()).cumsum()

    # Add columns of ones.
    grp['ones'] = 1

    # Loop through columns and update the mask.
    for col in df.columns:

        mask.loc[:, col] = (
                (grp.groupby(col)['ones'].transform('count') <= limit)
                | df[col].notnull()
        )

    # Now, interpolate and use the mask to create NaNs for the larger
    # gaps.
    method = getattr(df, fill_method)
    out = method(limit=limit, **fill_method_kwargs)[mask]

    # Be nice to the caller and return a Series if that's what they
    # provided.
    if isinstance(df_or_series, pd.Series):
        # Return a Series.
        return out.loc[:, out.columns[0]]

    return out


def filter_streamflow_1(data_dict=None,settings={ 'N': 14, 'nodata': 'NA' },silent=True):

    """
        Gapfilling of  streamflow data.

        Definition
        ----------
        def filter_streamflow_1(data_dict=None,settings={ 'N': 14, 'nodata': 'NA' },silent=True):


        Input               Format          Description
        -----               -----           -----------
        data_dict           dict            Data dictionary as returned by read_concentration():
                                            data = { <station_id_1>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     <station_id_2>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     ... }
                                            Default: None

        settings            dict            Maximum number of datapoints 'N' allowed to be missing
                                            between two available obersvations such that gap will
                                            be filled using linear interpolation. If gap is larger,
                                            it will not be filled.
                                            Value that was used to fill in no data values 'nodata'.
                                            Default: { 'N': 14, 'nodata': 'NA' }

        silent              Boolean         If set to True, nothing will be printed to terminal.
                                            Default: True


        Output              Format          Description
        -----               -----           -----------
        data_dict_filtered  dict            Data dictionary with same structure as inputs but filtered.


        Description
        -----------
        Gapfills streamflow data when less than N days of data are missing between two data points.
        Gaps will be filled through linear interpolation between the two given points. N is defined
        through settings but should realistically be 14 days or less.


        Restrictions
        ------------
        None.


        Examples
        --------

        Fill gaps

        >>> data_dict = {}
        >>> data_dict = filter_concentration_2(data_dict=data_dict,silent=True)
        >>> print("data_dict = {}".format(data_dict))
        data_dict = {}

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
        Written,  Juliane Mai, January 2023
    """

    # initialized return
    data_dict_filtered = {}

    # checking inputs
    if data_dict is None:
        raise ValueError("filter_streamflow_1: Dictionary containing data (data_dict) needs to be specified.")
    if settings is None:
        raise ValueError("filter_streamflow_1: Settings need to be specified.")
    if not( all([ ia in ['N', 'nodata'] for ia in settings.keys() ]) ):
        raise ValueError("filter_streamflow_1: Not all madatory settings specified. Mandatory is {} but only found {}.".format(['N', 'nodata'], settings.keys()))

    # fill in missing dates as NODATA in incoming dictionary
    new_data_dict = {}
    stations = list(data_dict.keys())
    for station in stations:
        dates = np.sort(list(data_dict[station].keys()))
        tmp_dict = {}
        for iidata,idata in enumerate(dates):

            curr_date = datetime.datetime(int(dates[iidata  ][0:4]),int(dates[iidata  ][5:7]),int(dates[iidata  ][8:10]),0,0)

            if iidata > 0:

                prev_date = datetime.datetime(int(dates[iidata-1][0:4]),int(dates[iidata-1][5:7]),int(dates[iidata-1][8:10]),0,0)
                tdelta = (curr_date-prev_date).days
                if tdelta > 1:
                    for itdelta in range(1,tdelta):
                        fill_date = prev_date + datetime.timedelta(days=itdelta)
                        fill_date = fill_date.strftime('%Y-%m-%d')
                        tmp_dict[fill_date] = { 'val': settings['nodata'], 'sym': None }

            if data_dict[station][idata]['val'] is None:
                # data can also be None in HYDAT database
                tmp_dict[idata] = { 'val': settings['nodata'], 'sym': None }
            else:
                # this is finally a real datapoint
                tmp_dict[idata] = data_dict[station][idata]

        new_data_dict[station] = tmp_dict

    # replace incoming data dict with the one that has now all dates
    data_dict = new_data_dict

    # initialize
    data_dict_filtered = {}
    stations = list(data_dict.keys())
    for station in stations:

        #print('station: ',station)

        nfiltered = 0

        data_dict_filtered_tmp = {}
        dates = list(data_dict[station].keys())

        vals_before = np.array([ float(data_dict[station][date]['val']) if (data_dict[station][date]['val'] != settings['nodata']) else np.nan  for date in dates ])
        mask_before = np.array([ data_dict[station][date]['val'] == settings['nodata'] for date in dates ])

        if np.any(mask_before):

            data = pd.DataFrame(
                index=dates,
                data={'station': vals_before})

            #print('data before: ',data)
            data = fill_with_hard_limit(data, int(settings['N']))
            #print('data after: ',data)

            # ---------------------------
            # take care of leading NaN
            # ---------------------------
            if ( np.isnan(data['station'].loc[dates[0]]) ):

                # found leading Nan
                # check if there is less than N leading nan
                count = 1
                while np.isnan(data['station'].loc[dates[count]]):
                    count += 1

                if count <= int(settings['N']):

                    # don not fill leading if data are [nan nan nan 1.0 nan ...] --> no dx available
                    if not( np.isnan(data['station'].loc[dates[count+1]] ) ):
                        dx = data['station'].loc[dates[count+1]] - data['station'].loc[dates[count]]
                        if not(silent): print("dx = ",dx)
                        for icount in range(count):
                            data['station'].loc[dates[icount]] = data['station'].loc[dates[count]] - (count-icount)*dx

            # ---------------------------
            # take care of trailing NaN
            # ---------------------------
            if ( data_dict[station][dates[-1]]['val'] == settings['nodata'] ):

                # found leading NaN (in original data)
                # check if there is less than N leading nan
                count = 1
                while ( data_dict[station][dates[-(count+1)]]['val'] == settings['nodata'] ):
                    count += 1

                if count <= int(settings['N']):

                    # don not fill leading if data are [... nan 1.0 nan nan nan] --> no dx available
                    if not( np.isnan(data['station'].loc[dates[-(count+2)]] ) ):
                        dx = data['station'].loc[dates[-(count+1)]] - data['station'].loc[dates[-(count+2)]]
                        if not(silent): print("dx = ",dx)
                        for icount in range(count):
                            #print("data['station'].loc[dates[-{}]] = {} + {}*{}".format(icount+1,data['station'].loc[dates[-(count+1)]],(count-icount),dx))
                            data['station'].loc[dates[-(icount+1)]] = data['station'].loc[dates[-(count+1)]] + (count-icount)*dx

                else:

                    for icount in range(count):
                        data['station'].loc[dates[-(icount+1)]] = np.nan

            for date in dates:
                if np.isnan( data['station'].loc[date] ):
                    data_dict_filtered_tmp[date] = {'val': settings['nodata'], 'sym': data_dict[station][date]['sym'] }
                else:
                    data_dict_filtered_tmp[date] = {'val': data['station'].loc[date], 'sym': data_dict[station][date]['sym'] }

            #print('data_dict_filtered_tmp: ',data_dict_filtered_tmp)

        else:

            data_dict_filtered_tmp = data_dict[station]

        vals_after = np.array([ float(data_dict_filtered_tmp[date]['val'])
                                    if (data_dict_filtered_tmp[date]['val'] != settings['nodata'])
                                    else np.nan for date in dates ])
        mask_after = np.array([ data_dict_filtered_tmp[date]['val'] == settings['nodata'] for date in dates ])

        nfiltered = np.sum(mask_before) - np.sum(mask_after)
        if not(silent): print("Filter 1: Station {}: Number of datapoints that were gap-filled = {}".format(station, nfiltered))

        data_dict_filtered[station] = data_dict_filtered_tmp

    return data_dict_filtered




def filter_streamflow_2(data_dict=None,settings=None,silent=True):

    """
        Filters streamflow data by .... (just placeholder right now)

        Definition
        ----------
        def filter_streamflow_2(data_dict=None):


        Input               Format          Description
        -----               -----           -----------
        data_dict           dict            Data dictionary as returned by read_streamflow():
                                            data = { <station_id_1>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     <station_id_2>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     ... }
                                            Default: None

        settings            dict            Specify necessary settings ....
                                            Default: None

        silent              Boolean         If set to True, nothing will be printed to terminal.
                                            Default: True


        Output              Format          Description
        -----               -----           -----------
        data_dict_filtered  dict            Data dictionary with same structure as inputs but filtered.


        Description
        -----------
        Filters data dictionary using ... (just placeholder).


        Restrictions
        ------------
        None.


        Examples
        --------

        Find periods

        >>> data_dict = {}
        >>> data_dict = filter_streamflow_2(data_dict=data_dict,silent=True)
        >>> print("data_dict = {}".format(data_dict))
        data_dict = {}


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
        Written,  Juliane Mai, January 2023
    """

    # initialized return
    data_dict_filtered = {}

    # checking inputs
    if data_dict is None:
        raise ValueError("filter_streamflow_2: dictionary containing data (data_dict) needs to be specified.")

    data_dict_filtered = data_dict

    # do something here with data_dict_filtered

    return data_dict_filtered




def filter_streamflow(data_dict=None,use_filter=None,settings=None,silent=True):

    """
        Applies several fiters to streamflow data.

        Definition
        ----------
        def filter_streamflow(data_dict=None,use_filter=None,settings=None,silent=True):


        Input               Format          Description
        -----               -----           -----------
        data_dict           dict            Data dictionary as returned by read_streamflow():
                                            data = { <station_id_1>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     <station_id_2>: { <date_1>: <value_1>,
                                                                       <date_2>: <value_2>,
                                                                       ... },
                                                     ... }
                                            Default: None

        use_filter          list            Lists the filters to be applied. The filters are
                                            applied in the order they are specified. A filter
                                            can appear multiple times if filter should be
                                            applied several times. If nothing is specified (None)
                                            a predefined set of filters is applied.
                                            Default: None (pre-defined set of filters applied)

        settings            dict            Specify settings for individual filters. Expected format:
                                            settings = { 'filter_1': {'N': 14, 'nodata': 'NA'},
                                                         'filter_2': None }
                                            Default: None

        silent              Boolean         If set to True, nothing will be printed to terminal.
                                            Default: True


        Output              Format          Description
        -----               -----           -----------
        data_dict_filtered  dict            Data dictionary with same structure as inputs but filtered.


        Description
        -----------
        Filters data dictionary by applying the filters specified. Filters can appear multiple times.
        They are applied in the order they are specified.


        Restrictions
        ------------
        None.


        Examples
        --------

        Find periods

        >>> data_dict = {}
        >>> settings = { 'filter_1': {'N': 14, 'nodata': 'NA'}, 'filter_2': None }
        >>> data_dict = filter_streamflow(data_dict=data_dict,use_filter=[1,2,1],settings=settings,silent=True)
        >>> print("data_dict = {}".format(data_dict))
        data_dict = {}


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
        Written,  Juliane Mai, January 2023
    """

    # initialized return
    data_dict_filtered = {}

    # checking inputs
    if data_dict is None:
        raise ValueError("filter_streamflow: dictionary containing data (data_dict) needs to be specified.")

    if use_filter is None:
        # use all available filters
        filters = [1,2,1]   # applied filter #1, then #2, and then again #1 --> just a placeholder for now
    else:
        # use only the ones specified
        filters = use_filter

    if settings is None:
        raise ValueError("filter_streamflow: dictionary containing settings for each filter used need to be specified.")

    data_dict_filtered = data_dict
    for ifilter in filters:
        if ifilter == 1:
            if not( 'filter_1' in settings.keys() ):
                raise ValueError("filter_streamflow: dictionary of settings for filter_1 is missing.")
            data_dict_filtered = filter_streamflow_1(data_dict_filtered, settings=settings['filter_1'], silent=silent)
        elif ifilter == 2:
            if not( 'filter_2' in settings.keys() ):
                raise ValueError("filter_streamflow: dictionary of settings for filter_2 is missing.")
            data_dict_filtered = filter_streamflow_2(data_dict_filtered, settings=settings['filter_2'], silent=silent)
        else:
            raise ValueError("filter_streamflow: filter {} is not defined yet.".format(ifilter))

    return data_dict_filtered



if __name__ == '__main__':
    #import doctest
    #doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    # source   = 'usgs'
    # filename = None
    # station  = '04069500,04084500,04085200,04087000,04096015'
    # info = get_info_station(source=source,filename=filename,station=station,silent=False)

    source   = 'usgs'
    filename = None
    station  = '04069500,04084500,04085200,04087000,04096015'
    station  = '01111230'
    data_streamflow = read_streamflow(source=source,filename=filename,station=station,silent=False)
