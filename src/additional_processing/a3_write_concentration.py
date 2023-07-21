#!/usr/bin/env python
from __future__ import print_function

# Copyright 2022-2023 Juliane Mai - contact[at]juliane-mai(dot)com
#
# License
# This file is part of the PWQMN toolbox library which contains scripts to
# retrieve raw PWQMN data, preprocessing them, run models using these data,
# or analysing the data in any other shape or form..
#
# The PWQMN code library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# The PWQMN code library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with The PWQMN code library.
# If not, see <https://github.com/julemai/PWQMN/blob/main/LICENSE>.

from pathlib2 import Path
import re
import numpy as np
import datetime as datetime


__all__ = ['write_concentration_csv']


def write_concentration_csv(data_dict=None,basename='../output/concentration_',nodata=None,period=None,station=None,silent=True):

    """
        Writes PWQMN data to a CSV.


        Definition
        ----------
        def write_concentration_csv(data_dict=None,basename='../output/concentration_',write_symbol=False,nodata=None,period=None,station=None,silent=True):


        Input           Format          Description
        -----           -----           -----------
        data_dict       dict            Data dictionary as returned by read_concentration():
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
                                        in, for example, '../output/concentration_04001302702.csv'.
                                        Default: '../output/concentration_'

        nodata          float or        Value to fill in in case data value is 'None' in PWQMN or
                        int or          date is missing entirely in PWQMN.
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
        Writes concentration data to a file. The data can be cropped to a time period specifying 'period'; the
        default is that all available data will be written. Missing data can be filled in by specifying a
        float as 'nodata' or skipped by setting 'nodata' to None (default).


        Restrictions
        ------------
        If first available date is past the 'start' date specified in 'period' or the last available date is
        prior to 'end' date specified in 'period' those "missing" dates will not be filled.


        Examples
        --------

        Read data from DataStream

        >>> from a2_read_concentration import read_concentration
        >>> source   = 'datastream'
        >>> filename = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN.csv'
        >>> variable = 'Inorganic nitrogen (nitrate and nitrite)'
        >>> station  = '16018403202'
        >>> data_pwqmn = read_concentration(source=source,filename=filename,station=station,variable=variable,pairsfile=None,silent=True)

        Write data from DataStream

        >>> basename     = '../output/daily_concentration_'
        >>> nodata       = None
        >>> station      = '16018403202'
        >>> period       = None # {'start':'1985-01-01','end':'2004-12-31'}
        >>> filenames_pwqmn = write_concentration_csv(data_dict=data_pwqmn,basename=basename,nodata=nodata,station=station,period=period,silent=True)
        >>> print("filenames_pwqmn = {}".format(filenames_pwqmn))
        filenames_pwqmn = {'16018403202': '../output/daily_concentration_16018403202.csv'}



        License
        -------
        This file is part of the PWQMN toolbox library which contains scripts to
        retrieve raw PWQMN data, preprocessing them, run models using these data,
        or analysing the data in any other shape or form..

        The PWQMN code library is free software: you can redistribute it and/or modify
        it under the terms of the GNU Lesser General Public License as published by
        the Free Software Foundation, either version 2.1 of the License, or
        (at your option) any later version.

        The PWQMN code library is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        GNU Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public License
        along with The PWQMN code library.
        If not, see <https://github.com/julemai/PWQMN/blob/main/LICENSE>.

        Copyright 2022-2023 Juliane Mai - juliane.mai@uwaterloo.ca


        History
        -------
        Written,  Juliane Mai, November 2022
    """

    # initialize return
    filenames = {}

    # checking inputs
    if data_dict is None:
        raise ValueError("write_concentration_csv: dictionary containing data (data_dict) needs to be specified.")

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
        ff.write("date_YYYY-MM-DD,remarkCode,{}_{} \n".format(data_dict[istation]['variable'].replace(' ','_'),data_dict[istation]['unit']))

        # collect data into lists
        dates = np.array([ ii                      for ii in data_dict[istation].keys() if not(ii in ['unit','variable']) ])
        data  = np.array([ data_dict[istation][ii] for ii in data_dict[istation].keys() if not(ii in ['unit','variable']) ])

        # make sure data are sorted according to dates
        idx = np.argsort(dates)
        dates = dates[idx]
        data  = data[idx]

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
                    ff.write(dates[iidata]+","+","+str(data[iidata])+" \n")
            else:
                # dates missing (i.e., gap to previous date) --> fill with NODATA
                if iidata > 0:
                    prev_date = datetime.datetime(int(dates[iidata-1][0:4]),int(dates[iidata-1][5:7]),int(dates[iidata-1][8:10]),0,0)
                    tdelta = (curr_date-prev_date).days
                    if tdelta > 1:
                        for itdelta in range(1,tdelta):
                            fill_date = prev_date + datetime.timedelta(days=itdelta)
                            fill_date = fill_date.strftime('%Y-%m-%d')
                            ff.write(fill_date+","+","+str(nodata)+" \n")


                # if NODATA vlaue is given, line where data=None will be filled in with NODATA value
                if not(data[iidata] is None):
                    ff.write(dates[iidata]+","+","+str(data[iidata])+" \n")
                else:
                    ff.write(dates[iidata]+","+","+str(nodata)+" \n")



        # close the file
        ff.close()

        if not(silent): print("Wrote concentration file: {}".format(outfile))

    # return list of names of files created
    return filenames


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    # from a2_read_concentration import read_concentration

    # source    = 'datastream'
    # filename  = '../data/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv'
    # variable  = 'Inorganic nitrogen (nitrate and nitrite)'   #'Chloride'
    # station   = '16018403202'
    # pairsfile = None
    # # station   = None
    # # pairsfile = '../data/Q_C_pairs.csv'

    # # read data
    # data_station = read_concentration(source=source,filename=filename,station=station,variable=variable,pairsfile=pairsfile,silent=True)

    # # write data
    # files_station = write_concentration_csv(data_dict=data_station,basename='../output/concentration_',nodata=None,period=None,station=station,silent=False)
