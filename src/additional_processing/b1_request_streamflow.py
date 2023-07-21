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


import os
from pathlib2 import Path

__all__ = ['request_streamflow']

def request_streamflow(source=None,filename=os.path.join('..', '..', 'data', 'observations', 'streamflow', 'Hydat.sqlite3'),silent=True):
    """
        Request streamflow dataset from different sources. For now this is a manual download.

        Definition
        ----------
        def request_streamflow(source=None,filename='../data/observations/streamflow/Hydat.sqlite3',silent=True):


        Input           Format          Description
        -----           -----           -----------
        source          string          Name of source to where to STREAMFLOW data were retrieved from.
                                        Currently implemented:
                                        hydat ... sqlite3 database retrieved from
                                                  http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/
                                        <more to follow>
                                        Default: None

        filename        string          Name of HYDAT database file.
                                        Default: '../data/observations/streamflow/Hydat.sqlite3'

        silent          Boolean         If set to True, nothing will be printed to terminal.
                                        Default: True


        Output          Format          Description
        -----           -----           -----------
        filename        string          Name of database file. None is returned if file does not exist.


        Description
        -----------
        Requests STREAMFLOW file. For now it only checks if file exists and provides information if it does not.


        Restrictions
        ------------
        Manual download required for now.


        Examples
        --------

        >>> source = 'hydat'
        >>> request = request_streamflow(source=source,filename='../data/observations/streamflow/Hydat.sqlite3',silent=True)
        >>> print("Requested file: {}".format(request))
        Requested file: ../data/observations/streamflow/Hydat.sqlite3


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
        raise ValueError("request_streamflow: source needs to be specified")

    # make sure source is implemented
    sources = ['hydat']
    if not(source in sources):
        raise ValueError('read_streamflow: Source not implemented yet. Needs to be one of the following: {}'.format(sources))

    if source == 'hydat':

        url = "http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/"
        if Path(filename).exists:
            if not(silent):
                print("Streamflow file successfully located ({}). You might want to check if there is a newer ".format(filename)+
                      "version available under {}. Then unzip that file and place it under {}.".format(url,filename))
            return filename
        else:
            if not(silent):
                print("Streamflow data not found under {}. Please download the zipped sqlite3 database from {}. "+
                      "Then unzip that file and save it under the following name in the data folder: {}.".format(filename,url,filename))
            return None

    else:
        raise ValueError("request_streamflow: source needs to be one of the following: {}".format(sources))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
