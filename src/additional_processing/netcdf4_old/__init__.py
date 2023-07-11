#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .netcdf4 import NcDataset, NcGroup, NcVariable, NcDimension
from .utils import concatDimension   # regular merge files (used for CaSPAr; does not take into account reference date)
from .utils import concatDimension2  # Julie's merge files (used to merge CaSPAr files with different reference dates)
