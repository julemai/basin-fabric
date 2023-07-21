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



# from __config_private import DATASTREAM_API_KEY
# import urllib.request
# import requests
# import warnings
# import json

from pathlib import Path


__all__ = ['request_concentration']


def request_concentration(source=None,filename='../../data/observations/nutrients/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv',silent=True):
    """
        Request concentration dataset from different sources. For now this is a manual download.

        Definition
        ----------
        def request_concentration(source=None,filename='../data/observations/nutrients/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv',silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to CONCENTRATION data were retrieved from.
                                        Currently implemented:
                                        datastream ... CSV file retrieved from
                                                       https://greatlakesdatastream.ca/explore/#/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba/
                                                       (see pre-processing information under ../data/observations/nutrients/README.md)
                                        <more to follow>
                                        Default: None

        filename        string          Name of DataStream database file.
                                        Default: '../data/observations/nutrients/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv'

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        filename        string          Name of database file. None is returned if file does not exist.


        Description
        -----------
        Requests CONCENTRATION file. For now it only checks if file exists and provides information if it does not.


        Restrictions
        ------------
        Manual download required for now since DataStream API does not work.


        Examples
        --------

        >>> source = 'datastream'
        >>> request = request_concentration(source=source,filename='../data/observations/nutrients/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv',silent=True)
        >>> print("Requested file: {}".format(request))
        Requested file: ../data/observations/nutrients/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv


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

    # check inputs
    if source is None:
        raise ValueError("request_concentration: source needs to be specified")

    # make sure source is implemented
    sources = ['datastream']
    if not(source in sources):
        raise ValueError('read_concentration: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'datastream':

        url = "https://greatlakesdatastream.ca/explore/#/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba/"
        if Path(filename).exists:
            if not(silent):
                print("Concentration file successfully located ({}). You might want to check if there is a newer ".format(filename)+
                      "version available under {}. Then pre-process file (see ../data/observations/nutrients/README.md) and place it under {}.".format(url,filename))
            return filename
        else:
            if not(silent):
                print("Concentration data not found under {}. Please download the CSV file from {}. "+
                      "Then pre-process the file (see ../data/observations/nutrients/README.md) and save it under the following name in the data folder: {}.".format(filename,url,filename))
            return None

    else:
        raise ValueError("request_concentration: source needs to be one of the following: {}".format(sources))



# def request_concentration(source=None,filename='/tmp/test',overwrite=False,silent=True):
#     """
#         Request PWQMN dataset from different sources.

#         --------------------------
#         Data from DataStream
#         --------------------------

#         1. REQUEST API key

#         Description:
#              https://github.com/datastreamapp/api-docs
#         Link to request key (might change):
#              https://docs.google.com/forms/d/1SjPVeblz2QFaghpiBZPZKOVNKXgw5UMnAtJLJS1tQYI

#         2. REQUEST DATA

#         Description:
#              https://datastream.org/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba

#         Use API to request data:
#              https://api.datastream.org/v1/odata/v4/Observations?$filter=DOI%20eq%20%2710.25976%2Ftnw0-3x43%27&$top=2
#              curl -G https://api.datastream.org/v1/odata/v4/Observations --data-urlencode "\$filter=DOI eq '10.25976/tnw0-3x43'" -H "x-api-key: PRIVATE-API-KEY"

#         --------------------------
#         Data from XXXX
#         --------------------------

#         <add more>



#         Definition
#         ----------
#         def request_concentration(source=None,filename='/tmp/test',overwrite=False,silent=False):


#         Input           Format          Description
#         -----           -----           -----------
#         source          string          Name of source to where to retrieve data from. Can also be
#                         or              a list of products in case several are supposed to be read
#                         list(string)    at the same time. Currently implemented:
#                                         datastream ... retrieves data from
#                                                        https://datastream.org/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba
#                                         <more to follow>
#                                         Default: None

#         filename        string          Filename of where to store retrieved file. The filename
#                                         can include a path. No file ending is supposed to be
#                                         specified. The files created will be of pattern:
#                                         <filename>_<source>.json
#                                         Default: "/tmp/test"

#         overwrite       Boolean         If file already exists at specified location (filename) it
#                                         will not be overwritten; unless overwrite is set to True.
#                                         Default: False

#         silent          Boolean         If set to True, nothing will be printed to terminal.
#                                         Default: True

#         Output          Format          Description
#         -----           -----           -----------
#         filenames       dict            Dictionary with the filename containing all the data read:
#                                         filenames = { source_0: filename_0,
#                                                       source_1: filename_1,
#                                                       ... }
#                                         filenames[source[0]] = <filename>_<source[0]>.json
#                                         filenames[source[1]] = <filename>_<source[1]>.json
#                                         ...


#         Description
#         -----------
#         Retrieves PWQMN data from multiple sources, standardizes the data into a format that is the
#         same across all sources, and returns a dictionary that contains all these filenames. One file
#         per source is created. The files always contain JSON strings with the same keys across all
#         files/sources.


#         Restrictions
#         ------------
#         Source: DataStream.
#                 - expects an API key to be requested first (see description and links above)
#                 - save this API key in file "src/config_private.py" under "DATASTREAM_API_KEY"

#         Examples
#         --------

#         Request data from DataStream (1 file)

#         >>> filename = 'test-data/test_20221110'
#         >>> files_pwqmn = request_concentration(source='datastream',filename=filename,overwrite=False,silent=True)
#         >>> print('files_pwqmn = '+str(files_pwqmn))
#         files_pwqmn = {'datastream': 'test-data/test_20221110_datastream.json'}


#         License
#         -------
#         This file is part of the PWQMN toolbox library which contains scripts to
#         retrieve raw PWQMN data, preprocessing them, run models using these data,
#         or analysing the data in any other shape or form..

#         The PWQMN code library is free software: you can redistribute it and/or modify
#         it under the terms of the GNU Lesser General Public License as published by
#         the Free Software Foundation, either version 2.1 of the License, or
#         (at your option) any later version.

#         The PWQMN code library is distributed in the hope that it will be useful,
#         but WITHOUT ANY WARRANTY; without even the implied warranty of
#         MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#         GNU Lesser General Public License for more details.

#         You should have received a copy of the GNU Lesser General Public License
#         along with The PWQMN code library.
#         If not, see <https://github.com/julemai/PWQMN/blob/main/LICENSE>.

#         Copyright 2022-2023 Juliane Mai - juliane.mai@uwaterloo.ca


#         History
#         -------
#         Written,  Juliane Mai, November 2022
#     """

#     # checking inputs
#     if source is None:
#         raise ValueError("request_concentration: source needs to be specified")

#     # make sure date input is always list
#     sources = ['datastream']
#     if not(source in sources):
#         raise ValueError('request_concentration: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

#     # make sure API key is set for DataStream
#     if 'datastream' in sources:
#         if not(DATASTREAM_API_KEY.isalnum()):
#             raise ValueError('request_concentration: Your API key for DataStream specified as DATASTREAM_API_KEY in "config_private.py" does not seem to be a valid API key. Please request an API key through "https://docs.google.com/forms/d/1SjPVeblz2QFaghpiBZPZKOVNKXgw5UMnAtJLJS1tQYI" and save that private key in that file.')

#     # initialize return
#     filenames = {}

#     for source in sources:

#         # filename including file extension and source
#         ifilename = filename+"_"+source+".json"

#         # data are read through DataStream API
#         if source == 'datastream':

#             if not(silent): print('\nDatastream')

#             if overwrite or not( Path(ifilename).is_file() ):

#                 # create request string
#                 api_str = 'https://api.datastream.org/v1/odata/v4/Observations?$filter=DOI%20eq%20%2710.25976%2Ftnw0-3x43%27&$top=2'
#                 if not(silent): print("   Downloading:        {}".format(api_str))

#                 headers = {'x-api-key': '{0}'.format(DATASTREAM_API_KEY)}
#                 response = requests.get(api_str, headers=headers)

#                 if check_status_datastream(response.status_code):

#                     # load data
#                     data = json.loads(response.content.decode('utf-8'))
#                     json_dump = json.dumps(data)

#                     print("data = ",data)

#                     # report some stats
#                     if not(silent): print("   Records downloaded: {}".format(len(data['value'])))

#                     # make sure folder to store file exists; otherwise create
#                     Path(ifilename).parent.mkdir(parents=True, exist_ok=True)

#                     # write to file
#                     ff_out = open(ifilename,"w")
#                     ff_out.write(json_dump)
#                     ff_out.close()
#                     if not(silent): print("   Wrote file:         {}".format(ifilename))

#                 else:
#                     data = {}

#                 # append source to return
#                 filenames[source] = ifilename

#             else:
#                 warnings.warn("request_concentration: File '{}' already exists. Will not be downloaded again.".format(ifilename))

#                 # append file to return
#                 filenames[source] = ifilename

#         # read data from other source
#         # elif source == 'XXX':
#         #

#         else:
#             raise ValueError('request_concentration: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

#     return filenames


# def check_status_datastream(status_code):

#     # checks response status when data are requested from DataStream

#     if (status_code == 413):
#         raise ValueError('request_concentration: status_code=413: Payload too Large.Try lowering $top or only pulling the values you need')
#     elif (status_code == 504):
#         raise ValueError('request_concentration: status_code=504: Timeout. Lowering $top or narrowing your search criteria should resolve your issue')
#     elif (status_code == 502):
#         raise ValueError('request_concentration: status_code=502: Bad Gateway. Please ensure that your path is correct')
#     elif (status_code == 500):
#         raise ValueError('request_concentration: status_code=500: Internal Server Error. Please contact the DataStream team')
#     elif (status_code == 403):
#         raise ValueError('request_concentration: status_code=403: Forbidden. Please ensure that your api token is correct')
#     elif (status_code == 400):
#         raise ValueError('request_concentration: status_code=400: Bad Request. Please ensure that proper filters and selects are being passed')
#     elif (status_code == 408):
#         raise ValueError('request_concentration: status_code=408: Timeout.')
#     elif (status_code == 200):
#         return( True )
#     else:

#         raise ValueError('request_concentration: status_code={}: Please contact the DataStream team'.format(status_code))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

    # source    = 'datastream'
    # filename  = 'test-data/test'
    # overwrite =  True
    # silent    =  False
    # request_concentration(source=source,filename=filename,overwrite=overwrite,silent=silent)
