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
import re
import warnings
import numpy as np


__all__ = ['get_info_station', 'read_concentration', 'filter_concentration']


def get_info_station(source=None,filename='/tmp/test',station=None,pairsfile=None,silent=True):
    """
        Reads PWQMN data file and returns information for given station, i.e.,
        variables and time period those variables are available for.

        Definition
        ----------
        def get_info_station(source=None,filename='/tmp/test',station=None,pairsfile=None,silent=False):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to PWQMN data were retrieved from.
                                        Currently implemented:
                                        datastream ... data retrieved from
                                                       https://datastream.org/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        station         string          Station ID to read and obtain unique list of available variables from.
                                        Either station or pairsfile needs to be specified.
                                        Default: None

        pairsfile       string          Name of file containing pairs of streamflow and concentration stations.
                                        Format:
                                        ---> C station ID,Q station ID,Name,LAT,LONG,Area(km2)
                                        Default: None

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        info            dict            Dictionary with unique sets of avaialable variables and time period
                                        data are available for.
                                        info = { var_1: {start: YYYY-MM-DD, end: YYYY-MM-DD},
                                                 var_2: {start: YYYY-MM-DD, end: YYYY-MM-DD},
                                                 ...
                                               }


        Description
        -----------
        Reads data and returns dictionary of variables (including start and end date)
        available for the specified station.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read data from DataStream file

        >>> source   = 'datastream'
        >>> filename = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN.csv'
        >>> station  = '16018403202'
        >>> info = get_info_station(source=source,filename=filename,station=station,silent=True)
        >>> print("info[{}][{}] = {}".format(station,'"Alkalinity, total"',info[station]['"Alkalinity, total"']))
        info[16018403202]["Alkalinity, total"] = {'start': '1970-05-26', 'end': '2010-05-26', 'unit': 'mg/l'}
        >>> print("info[{}][{}] = {}".format(station,'Chloride',info[station]['Chloride']))
        info[16018403202][Chloride] = {'start': '1970-05-26', 'end': '2018-08-29', 'unit': 'mg/l'}


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

    if source is None:
        raise ValueError("get_info_station: source needs to be specified")

    if (station is None) and (pairsfile is None):
        raise ValueError("get_info_station: either station or pairsfile needs to be specified")
    elif not(station is None) and not(pairsfile is None):
        raise ValueError("get_info_station: either station or pairsfile needs to be specified. not both.")
    elif not(station is None):
        stations = [ station ]
    elif not(pairsfile is None):
        # open file and read content
        ff = open(str(Path(pairsfile)), "r")
        lines = ff.readlines()
        ff.close()

        stations = []
        for ll in lines[1:]:
            stations.append(ll.strip().split(',')[0])  # [0] = C stations

    else:
        raise ValueError("get_info_station: Not sure what happened!")

    # make sure source is implemented
    sources = ['datastream']
    if not(source in sources):
        raise ValueError('get_info_station: Source not implemented yet. Needs to be one of the following: {}'.format(sources))


    if source == 'datastream':

        ff = open(str(Path(filename)), "r")
        lines = ff.readlines()
        ff.close()

        # split is more complicated (and takes longer)
        # because there's some fields in double-quotes
        # that contain commas that cant be split
        header = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', lines[0].strip()) # lines[0].strip().split(',')
        idx_station   = header.index('MonitoringLocationID')
        idx_variable1 = header.index('CharacteristicName')
        idx_variable2 = header.index('MethodSpeciation')
        idx_variable3 = header.index('ResultSampleFraction')
        idx_date      = header.index('ActivityStartDate')
        idx_value     = header.index('ResultValue')
        idx_unit      = header.index('ResultUnit')

        data = {}
        variables = {}
        for ll in lines[1:]:

            # split is more complicated (and takes longer)
            # because there's some fields in double-quotes
            # that contain commas that cant be split
            ll = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', ll.strip()) #ll.strip().split(',')

            station = ll[idx_station]
            if (station in stations) and (ll[idx_value] != ''):  # make sure value is not actually empty ''

                var = "{} {} {}".format(ll[idx_variable1],ll[idx_variable2],ll[idx_variable3]).strip()
                if station in data.keys():
                    if not(var in data[station].keys()):
                        # station already available but not this variable
                        data[station][var] = [ ll[idx_date] ]
                        # station already available but not this variable
                        variables[station][var] = ll[idx_unit]
                    else:
                        # some data for this variable and station already written
                        data[station][var].append( ll[idx_date] )
                else:
                    # no data for station yet written
                    tmp = {}
                    tmp[var] = [ ll[idx_date] ]
                    data[station] = tmp
                    # no data for station yet written
                    tmp = {}
                    tmp[var] = ll[idx_unit]
                    variables[station] = tmp


        for ss in data.keys():

            for vv in data[ss].keys():

                data[ss][vv] = { 'start': min(data[ss][vv]), 'end': max(data[ss][vv]), 'unit': variables[ss][vv] }

    return data

def convert(value, from_unit, to_unit):
    """
        Converts 'value' given in 'from_unit' to value given in 'to_unit'.
    """

    if from_unit == to_unit:
        return value
    else:
        if (from_unit == 'ug/l') and (to_unit == 'mg/l'):
            return value / 1000.
        elif (from_unit == 'mg/l') and (to_unit == 'ug/l'):
            return value * 1000.
        else:
            raise ValueError('Unit {} can not be converted to unit {}. Please implement conversion first.'.format(from_unit, to_unit))

def read_concentration(source=None,filename='/tmp/test',station=None,variable=None,unit='mg/l',prioritize=False,check=None,pairsfile=None,silent=True):
    """
        Reads data for a specific station(s) and variable. The stations can also be provided
        as a CSV file which specifies the pairs of concentration/streamflow gauge IDs.


        Definition
        ----------
        def read_concentration(source=None,filename='/tmp/test',station=None,variable=None,prioritize=False,pairsfile=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to PWQMN data were retrieved from.
                                        Currently implemented:
                                        datastream ... data retrieved from
                                                       https://datastream.org/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba
                                        <more to follow>
                                        Default: None

        filename        string          Name of file to read data from.
                                        Default: '/tmp/test'

        station         string          Station ID to read and obtain unique list of available variables from.
                                        Either station or pairsfile needs to be specified.
                                        Default: None

        variable        string or       Name of variable to read. Can be multiple. Order matters if prioritize=True.
                        list(string)    Default: None

        unit            string          Unit all values are assumed to be given in or otherwise will be converted to this unit.
                                        So far only 'ug/l' can be converted to 'mg/l'. More might be added as needed.
                                        Default: mg/l

        prioritize      Boolean         If set to True and multiple variables are specified only the observations of
                                        the variable with highest priority will be considered. Priority is determined
                                        by position of variable in list "variable", i.e., the first variable has highest
                                        priority, the last variable has lowest.
                                        If set to False all available observations will be averaged; no matter from which
                                        variable.
                                        Default: False

        check           dict            Dictionary specifying which variables need to be checked for consistency.
                                        Possible checks implemented are:
                                        (var_1 > var_2) and (var_4 > var_6):
                                           { 'greater_2v':      [{'var_1': <variable name>, 'var_2': <variable name>},
                                                                 {'var_1': <variable name>, 'var_2': <variable name>}] }
                                        var_1 >= var_2:
                                           { 'greaterequal_2v': [{'var_1': <variable name>, 'var_2': <variable name>}] }
                                        var_1 < var_2:
                                           { 'lessthan_2v':     [{'var_1': <variable name>, 'var_2': <variable name>}] }
                                        var_1 <= var_2:
                                           { 'lessequal_2v':    [{'var_1': <variable name>, 'var_2': <variable name>}] }
                                        Can only be used if 'prioritize=False' since prioritize only selects one variable
                                        anyway. If check is not satisfied because var_1 < var_2 even though it is required
                                        to be var_1 >= var_2, the data point will be discarded entirely.
                                        Default: None

        pairsfile       string          Name of file containing pairs of streamflow and concentration stations.
                                        Format:
                                        ---> C station ID,Q station ID,Name,LAT,LONG,Area(km2)
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
        Reads data of a station (or list of stations) for one specific variable from a PWQMN dataset.


        Restrictions
        ------------
        None.


        Examples
        --------

        Read data from DataStream

        >>> source   = 'datastream'
        >>> filename = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN.csv'
        >>> variable = 'Inorganic nitrogen (nitrate and nitrite)'
        >>> station  = '16018403202'
        >>> data_pwqmn = read_concentration(source=source,filename=filename,station=station,variable=variable,pairsfile=None,silent=True)
        >>> date = '2000-03-15'
        >>> print("data_pwqmn['16018403202']['{}'] = {}".format(date,data_pwqmn[station][date]))
        data_pwqmn['16018403202']['2000-03-15'] = 9.44
        >>> date = '2018-08-29'
        >>> print("data_pwqmn['16018403202']['{}'] = {}".format(date,data_pwqmn[station][date]))
        data_pwqmn['16018403202']['2018-08-29'] = 2.97
        >>> date = '1991-01-30'
        >>> print("data_pwqmn['16018403202']['{}'] = {}".format(date,data_pwqmn[station][date]))
        data_pwqmn['16018403202']['1991-01-30'] = 4.41


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
        raise ValueError("read_concentration: source needs to be specified")

    if (prioritize) and not(check is None):
        raise ValueError("read_concentration: Prioritization and variable checks are mutually exclusive and do not make sense to be used together. 'prioritize' is selcting exactly one variable while 'check' checks consitency between multiple (>1) variables. Please specify only one.")

    if (station is None) and (pairsfile is None):
        raise ValueError("read_concentration: either station or pairsfile needs to be specified")
    elif not(station is None) and not(pairsfile is None):
        raise ValueError("read_concentration: either station or pairsfile needs to be specified. not both.")
    elif not(station is None):
        stations = [ station ]
    elif not(pairsfile is None):
        # open file and read content
        ff = open(str(Path(pairsfile)), "r")
        lines = ff.readlines()
        ff.close()

        stations = []
        for ll in lines[1:]:
            stations.append(ll.strip().split(',')[0])  # C stations

    else:
        raise ValueError("read_concentration: Not sure what happened!")

    # make sure variable is always a list
    if isinstance(variable, str):
        variable = [ variable ]
    if not(isinstance(variable, list)):
        raise ValueError('The argument "variable" must be string or list of strings.')

    if not(silent): print("stations: ",stations)

    # make sure source is implemented
    sources = ['datastream']
    if not(source in sources):
        raise ValueError('read_concentration: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    # open file and read content
    ff = open(str(Path(filename)), "r")
    lines = ff.readlines()
    ff.close()

    # split is more complicated (and takes longer)
    # because there's some fields in double-quotes
    # that contain commas that cant be split
    # ----> takes really long
    # header = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', lines[0].strip())

    # we cleaned file from those double-quotes and commas within (are now semi-colons)
    # ----> much faster
    header = lines[0].strip().split(',')
    idx_station   = header.index('MonitoringLocationID')
    idx_variable1 = header.index('CharacteristicName')
    idx_variable2 = header.index('MethodSpeciation')
    idx_variable3 = header.index('ResultSampleFraction')
    idx_date      = header.index('ActivityStartDate')
    idx_value     = header.index('ResultValue')
    idx_unit      = header.index('ResultUnit')

    data = {}
    for ll in lines[1:]:

        # split is more complicated (and takes longer)
        # because there's some fields in double-quotes
        # that contain commas that cant be split
        # ----> takes really long
        # ll = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', ll.strip())

        # we cleaned file from those double-quotes and commas within (are now semi-colons)
        # ----> much faster
        ll = ll.strip().split(',')
        station = ll[idx_station]
        var = "{} {} {}".format(ll[idx_variable1],ll[idx_variable2],ll[idx_variable3]).strip()
        if (station in stations) and (var in variable) and (ll[idx_value] != ''):   # make sure value is not actually empty ''

            if not(silent): print("Found station: ",station)

            if not(station in data.keys()):
                data[station] = { 'variable': ' _OR_ '.join(variable),
                                  'unit': unit, #ll[idx_unit],
                                  # initialize
                                  ll[idx_date]: { vv: [] for vv in variable },
                                }
                # set value
                data[station][ll[idx_date]][var].append( convert( float(ll[idx_value]), ll[idx_unit], unit ) )
            else:
                # --> we try to convert units now
                #
                # if data[station]['unit'] != ll[idx_unit]:
                #     raise ValueError('Units not matching for station={}, variable={}, date={}. Previously set to {} but is now {}.'.format(
                #         station, var, ll[idx_date],data[station]['unit'], ll[idx_unit]))

                if ll[idx_date] in data[station].keys():
                    # append
                    data[station][ll[idx_date]][var].append( convert( float(ll[idx_value]), ll[idx_unit], unit ) )
                    warnings.warn('read_concentration: Found duplicate values for station={}, date={}, variable="{}": {}'.format(
                        station, ll[idx_date], ' _OR_ '.join(variable), data[station][ll[idx_date]]))
                else:
                    # initialize
                    data[station][ll[idx_date]] = { vv: [] for vv in variable }
                    # set value
                    data[station][ll[idx_date]][var].append( convert( float(ll[idx_value]), ll[idx_unit], unit ) )

    # now go through all collected data and average
    stations = list(data.keys())
    for station in stations:
        dates = list(data[station].keys())
        dates.remove('variable')   # this was stupid --> will change soon
        dates.remove('unit')       # this was stupid --> will change soon
        for date in dates:
            #print("data[{}][{}] = {}".format(station,date,data[station][date]))

            check_passed = True
            if prioritize:
                # go through all variables (in order) and look for first one with observations
                # one must be != [] otherwise "date" would not exist
                # data[station][date] = {'aa': [2,3], 'bb':[], 'cc':[4]} --> values_to_average = [2,3]
                values_to_average = []
                ivar = 0
                while values_to_average == []:
                    values_to_average = data[station][date][variable[ivar]]
                    ivar += 1
            else:

                # potentially check consistency of multiple variables
                # --> if check fails remove date from dictionary
                if not( check is None ):

                    check_names = check.keys()
                    for check_name in check_names:

                        ichecks = check[check_name]  # all checks to perform in one category

                        if check_name == 'greater_2v':

                            for iicheck,icheck in enumerate(ichecks):

                                var_1 = icheck['var_1']
                                var_2 = icheck['var_2']
                                if (var_1 in data[station][date].keys()) and (var_2 in data[station][date].keys()):
                                    #print("CHECKING data[{}][{}] = {}".format(station,date,data[station][date]))
                                    if (data[station][date][var_1] != []) and (data[station][date][var_2] != []):
                                        if not( np.min(data[station][date][var_1]) > np.max(data[station][date][var_2]) ): # min/max because several observations can exist
                                            check_passed = False
                                            print("Check '{}' testing '{}'>'{}' failed for station {} on {}.".format(check_name,var_1,var_2,station,date))

                        elif check_name == 'greaterequal_2v':

                            for iicheck,icheck in enumerate(ichecks):

                                var_1 = icheck['var_1']
                                var_2 = icheck['var_2']
                                if (var_1 in data[station][date].keys()) and (var_2 in data[station][date].keys()):
                                    #print("CHECKING data[{}][{}] = {}".format(station,date,data[station][date]))
                                    if (data[station][date][var_1] != []) and (data[station][date][var_2] != []):
                                        if not( np.min(data[station][date][var_1]) >= np.max(data[station][date][var_2]) ): # min/max because several observations can exist
                                            check_passed = False
                                            print("Check '{}' testing '{}'>='{}' failed for station {} on {}.".format(check_name,var_1,var_2,station,date))

                        elif check_name == 'lessthan_2v':

                            for iicheck,icheck in enumerate(ichecks):

                                var_1 = icheck['var_1']
                                var_2 = icheck['var_2']
                                if (var_1 in data[station][date].keys()) and (var_2 in data[station][date].keys()):
                                    #print("CHECKING data[{}][{}] = {}".format(station,date,data[station][date]))
                                    if (data[station][date][var_1] != []) and (data[station][date][var_2] != []):
                                        if not( np.min(data[station][date][var_1]) < np.max(data[station][date][var_2]) ): # min/max because several observations can exist
                                            check_passed = False
                                            print("Check '{}' testing '{}'<'{}' failed for station {} on {}.".format(check_name,var_1,var_2,station,date))

                        elif check_name == 'lessequal_2v':

                            for iicheck,icheck in enumerate(ichecks):

                                var_1 = icheck['var_1']
                                var_2 = icheck['var_2']
                                if (var_1 in data[station][date].keys()) and (var_2 in data[station][date].keys()):
                                    #print("CHECKING data[{}][{}] = {}".format(station,date,data[station][date]))
                                    if (data[station][date][var_1] != []) and (data[station][date][var_2] != []):
                                        if not( np.min(data[station][date][var_1]) <= np.max(data[station][date][var_2]) ): # min/max because several observations can exist
                                            check_passed = False
                                            print("Check '{}' testing '{}'<='{}' failed for station {} on {}.".format(check_name,var_1,var_2,station,date))

                        else:

                            raise ValueError("Check '{}' is not implemented yet!".format(check_name))


                # data[station][date] = {'aa': [2,3], 'bb':[], 'cc':[4]} --> values_to_average = [2,3,4]
                values_to_average = [ item for sublist in [ data[station][date][dd] for dd in data[station][date] ] for item in sublist ]

            # average now
            if check_passed:
                data[station][date] = np.mean( values_to_average )
            else:
                # if data point did not pass check, remove date entirely
                del data[station][date]

    return data


def filter_concentration_1(data_dict=None,silent=True):

    """
        Filters concentration data by removing observations that are negative.

        Definition
        ----------
        def filter_concentration_1(data_dict=None,silent=True):


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

        silent              Boolean         If set to True, nothing will be printed to terminal.
                                            Default: True


        Output              Format          Description
        -----               -----           -----------
        data_dict_filtered  dict            Data dictionary with same structure as inputs but filtered.


        Description
        -----------
        Filters concentration data by removing observations that are negative.


        Restrictions
        ------------
        None.


        Examples
        --------

        Filter data

        >>> data_dict = {}
        >>> data_dict = filter_concentration_1(data_dict=data_dict,silent=True)
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
        raise ValueError("filter_concentration_1: dictionary containing data (data_dict) needs to be specified.")

    # initialize
    data_dict_filtered = {}
    stations = list(data_dict.keys())
    for station in stations:

        nfiltered = 0

        data_dict_filtered_tmp = {'variable': data_dict[station]['variable'], 'unit': data_dict[station]['unit']}
        dates = list(data_dict[station].keys())
        dates.remove('variable')   # this was stupid --> will change soon
        dates.remove('unit')       # this was stupid --> will change soon
        for date in dates:

            # use only values that pass filter
            if data_dict[station][date] >= 0.0:
                data_dict_filtered_tmp[date] = data_dict[station][date]
            else:
                nfiltered += 1

        if not(silent): print("Filter 1: Station {}: Number of datapoints removed = {}".format(station, nfiltered))

        data_dict_filtered[station] = data_dict_filtered_tmp

    return data_dict_filtered


def filter_concentration_2(data_dict=None,silent=True):

    """
        Filters concentration data that are more than 4 standard deviations away from mean

        Definition
        ----------
        def filter_concentration_2(data_dict=None,silent=True):


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

        silent              Boolean         If set to True, nothing will be printed to terminal.
                                            Default: True


        Output              Format          Description
        -----               -----           -----------
        data_dict_filtered  dict            Data dictionary with same structure as inputs but filtered.


        Description
        -----------
        Filters concentration data that are more than 4 standard deviations away from mean


        Restrictions
        ------------
        None.


        Examples
        --------

        Filter data

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
        raise ValueError("filter_concentration_2: dictionary containing data (data_dict) needs to be specified.")

    # initialize
    data_dict_filtered = {}
    stations = list(data_dict.keys())
    for station in stations:

        nfiltered = 0

        data_dict_filtered_tmp = {'variable': data_dict[station]['variable'], 'unit': data_dict[station]['unit']}
        dates = list(data_dict[station].keys())
        dates.remove('variable')   # this was stupid --> will change soon
        dates.remove('unit')       # this was stupid --> will change soon

        mean = np.mean( [ data_dict[station][date] for date in dates ] )
        std  = np.std(  [ data_dict[station][date] for date in dates ] )

        if not(silent): print("Filter 2: Station {}: Data values between {} and {} will be removed.".format(station,mean-4*std,mean+4*std))
        for date in dates:

            # use only values that pass filter
            if (data_dict[station][date] < mean + 4.0 * std) and (data_dict[station][date] > mean - 4.0 * std):
                data_dict_filtered_tmp[date] = data_dict[station][date]
            else:
                nfiltered += 1

        if not(silent): print("Filter 2: Station {}: Number of datapoints removed = {}".format(station, nfiltered))

        data_dict_filtered[station] = data_dict_filtered_tmp

    return data_dict_filtered




def filter_concentration(data_dict=None,use_filter=None,silent=True):

    """
        Applies several fiters to concentration data.

        Definition
        ----------
        def filter_concentration(data_dict=None,use_filter=None,silent=True):


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

        use_filter          list            Lists the filters to be applied. The filters are
                                            applied in the order they are specified. A filter
                                            can appear multiple times if filter should be
                                            applied several times. If nothing is specified (None)
                                            a predefined set of filters is applied.
                                            Default: None (pre-defined set of filters applied)

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

        Filter data

        >>> data_dict = {}
        >>> data_dict = filter_concentration(data_dict=data_dict,use_filter=[1,2,1],silent=True)
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
        raise ValueError("filter_concentration: dictionary containing data (data_dict) needs to be specified.")

    if use_filter is None:
        # use all available filters
        filters = [1,2,1]   # applied filter #1, then #2, and then again #1 --> just a placeholder for now
    else:
        # use only the ones specified
        filters = use_filter

    data_dict_filtered = data_dict
    for ifilter in filters:
        if ifilter == 1:
            data_dict_filtered = filter_concentration_1(data_dict_filtered,silent=silent)
        elif ifilter == 2:
            data_dict_filtered = filter_concentration_2(data_dict_filtered,silent=silent)
        else:
            raise ValueError("filter_concentration: filter {} is not defined yet.".format(ifilter))

    return data_dict_filtered


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    # source    = 'datastream'
    # filename  = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv'
    # station   = '16018403202'
    # pairsfile = None
    # # station   = None
    # # pairsfile = '../data/Q_C_pairs.csv'
    # data_info = get_info_station(source=source,filename=filename,station=station,pairsfile=pairsfile,silent=True)


    # source    = 'datastream'
    # filename  = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv'
    # variable  = 'Inorganic nitrogen (nitrate and nitrite)'   #'Chloride'
    # station   = '16018403202'
    # pairsfile = None
    # # station   = None
    # # pairsfile = '../data/Q_C_pairs.csv'

    # # read data
    # data_station = read_concentration(source=source,filename=filename,station=station,variable=variable,pairsfile=pairsfile,silent=True)
