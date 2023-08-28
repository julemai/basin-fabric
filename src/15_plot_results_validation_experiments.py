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

# source env-3.10/bin/activate
# pyenv activate env-3.8.5-basin-fabric


# # MAP        :: plot results of LSTM experiment (lstm/<experiment>/hyper-parameter-tuning/*.csv)
# python 15_plot_results_validation_experiments.py -s 'conus-zhi'   -x 'conus-zhi-v1'
# python 15_plot_results_validation_experiments.py -s 'grip-gl-mai' -x 'grip-gl-mai-v2'

# # TIMESERIES + MAP :: plot only one experiment (regions/<region>/predictions/using_<using_lstm>/ensemble/test_ensemble_results.nc)
# python 15_plot_results_validation_experiments.py -s wisconsin-lewis -u conus-zhi-v1    -p 1980-01-01:2018-12-31
# python 15_plot_results_validation_experiments.py -s ontario-zhi     -u conus-zhi-v1    -p 1980-01-01:2018-12-31
# python 15_plot_results_validation_experiments.py -s conus-zhi       -u conus-zhi-v1    -p 1980-01-01:2018-12-31
# python 15_plot_results_validation_experiments.py -s grip-gl-mai     -u grip-gl-mai     -p 1980-01-01:2018-12-31

# # TIMESERIES + MAP :: plot all available validation experiments (regions/<case_study>/predictions/using_*/ensemble/test_ensemble_results.nc)
# python 15_plot_results_validation_experiments.py -s wisconsin-lewis   -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31
# python 15_plot_results_validation_experiments.py -s ontario-zhi       -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31
# python 15_plot_results_validation_experiments.py -s conus-zhi         -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31
# python 15_plot_results_validation_experiments.py -s grip-gl-mai       -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31
# python 15_plot_results_validation_experiments.py -s camels-us-newman  -p 2000-01-01:2018-12-31,1980-01-01:1999-12-31


"""

Plots results found in experiment onto a map or from validation experiments as timeseries.

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
Written,  JM, Jul 2023

"""

# -------------------------------------------------------------------------
# General settings
#
dobw      = False # True: black & white
docomp    = True  # True: Print classification on top of modules
dosig     = False  # True: add signature to plot
dolegend  = False # True: add legend to each subplot
doabc     = False # True: add subpanel numbering
dotitle   = True  # True: add catchment titles to subpanels


# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')
sys.path.append(dir_path+'/lib')

import pandas   as pd
import xarray   as xr
import numpy    as np
import glob     as glob
import time     as time
import datetime as datetime
import json     as json
import color                            # in lib/
from brewer        import get_brewer    # in lib/
from position      import position      # in lib/
from str2tex       import str2tex       # in lib/
from abc2plot      import abc2plot      # in lib/
from autostring    import astr          # in lib/
from errormeasures import nse, kge, rmse, mse, mae, pear2, bias   # in lib/

case_study   = None
experiment   = None
period       = None
using_lstm   = None
period       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']. Default: None.")
parser.add_argument('-x', '--experiment', action='store', default=experiment, dest='experiment',
                    help="Name of LSTM experiment . Resulting files plotted are 'lstm/<experiment>/hyper-parameter-tuning/*.csv.*'. Default: 'test'.")
parser.add_argument('-u', '--using_lstm', action='store', default=using_lstm, dest='using_lstm',
                    help="Name of region the LSTM was trained for which will be used to derive predictions for basins of case study (-s). Can be the same as case_study. Then basins will just be evaluated, e.g., for a longer time period. The name provided needs to be the name of a folder in 'lstm/'.")
parser.add_argument('-p', '--period', action='store', default=period, dest='period',
                    help="Period to retrieve data for. Format: YYYY-MM-DD:YYYY-MM-DD. ")

args         = parser.parse_args()
case_study   = args.case_study
experiment   = args.experiment
using_lstm   = args.using_lstm
period       = args.period

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']")

if not(period is None):
    periods = period.split(',')
    for iperiod,period in enumerate(periods):
        start = period.split(':')[0]
        start = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%Y-%m-%d') #"%d/%m/%Y")
        end   = period.split(':')[1]
        end   = datetime.datetime.strptime(end,   '%Y-%m-%d').strftime('%Y-%m-%d') #"%d/%m/%Y")
        periods[iperiod] = {'start':start, 'end':end, 'string':period}
    print('Number of periods found:               {}'.format(len(periods)))

if (experiment is None) and (using_lstm is None):
    # assuming that all validation experiments for case_study should be plotted
    using_lstm = 'all'

del parser, args





t1 = time.time()

project_root = Path(dir_path+'/../regions/'+case_study)

if not(using_lstm is None):
    if using_lstm == 'all':
        validation_results = glob.glob(dir_path+"/../regions/"+case_study+"/predictions/using_*/ensemble/test_ensemble_results.nc")
    else:
        validation_results = glob.glob(dir_path+"/../regions/"+case_study+"/predictions/using_"+using_lstm+"/ensemble/test_ensemble_results.nc")
    if len(validation_results) == 0:
        raise ValueError('No validation results found for region {}.'.format(case_study))

if case_study == 'wisconsin-lewis':
    llcrnrlon =  -93.0
    urcrnrlon =  -86.1
    llcrnrlat =   42.0
    urcrnrlat =   47.2
    parallels = np.arange( -80., 81., 2.)
    meridians = np.arange(-180.,181., 2.)

elif case_study == 'ontario-zhi':
    llcrnrlon =  -91.0
    urcrnrlon =  -73.0
    llcrnrlat =   40.5
    urcrnrlat =   49.8
    parallels = np.arange( -80., 81., 3.)
    meridians = np.arange(-180.,181., 5.)

elif case_study == 'conus-zhi':
    llcrnrlon =  -120.0
    urcrnrlon =  -60.0
    llcrnrlat =   20.5
    urcrnrlat =   51.5
    parallels = np.arange( -80., 81., 10.)
    meridians = np.arange(-180.,181., 15.)

elif case_study == 'camels-us-newman':
    llcrnrlon =  -120.0
    urcrnrlon =  -60.0
    llcrnrlat =   20.5
    urcrnrlat =   51.5
    parallels = np.arange( -80., 81., 10.),
    meridians = np.arange(-180.,181., 15.)

elif case_study == 'grip-gl-mai':
    llcrnrlon =  -93.0
    urcrnrlon =  -72.0
    llcrnrlat =   39.0
    urcrnrlat =   51.0
    parallels = np.arange( -80., 81., 3.),
    meridians = np.arange(-180.,181., 5.)

elif case_study == 'north-america-mai':
    llcrnrlon =  -116.   # lon: -131.36749999999995 to -60.98499999999996
    urcrnrlon =   -46.
    llcrnrlat =   18.    # lat: 26.920416654000064 to 59.33374999800003
    urcrnrlat =   58.
    parallels = np.arange( -80., 81., 10.),
    meridians = np.arange(-180.,181., 15.)

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))



if not( experiment is None):
    outfolder    = Path(project_root / '..' / '..' / 'lstm' / experiment / 'final-training' )

    # read observations
    df = xr.open_dataset(project_root / 'observations' / 'daily_streamflow.nc')

    # read basins.csv for (lat,lon,obs_q)
    static_attributes_basin   = pd.read_csv(project_root / 'basins.csv', index_col=[0],
                                                dtype={'id': 'str', 'name': 'str', 'lat': 'float', 'lon': 'float', 'obs_q': 'str'})

    # read results
    filenames = glob.glob( str(project_root / '..' / '..' / 'lstm' / experiment / 'final-training' / '*.csv.*') )
    filenames = [ ff for ff in filenames if ff[-4:] != '.png' ]  # filter out already existing PNGs
    dict_results = {}
    for filename in filenames:
        dict_results[Path(filename).name] = pd.read_csv( filename, index_col=[0], dtype={'basin': 'str', 'NSE_1D': 'float', 'KGE_1D': 'float'})

    gauge_dict = {}
    for basin in list(static_attributes_basin.index):

        if not(static_attributes_basin.loc[basin]['obs_q'] is np.nan):

            # kk ... current result file
            # mm ... metric available
            results = { kk: { mm: dict_results[kk].loc[basin][mm] for mm in list(dict_results[kk].loc[basin].index) } for kk in list(dict_results.keys()) }

            gauge_dict[static_attributes_basin.loc[basin]['obs_q']] = {
                'lat': static_attributes_basin.loc[basin]['lat'],
                'lon': static_attributes_basin.loc[basin]['lon'],
                'metrics': results,
                }
        else:
            print("No gauge found for basin {} ({}).".format(basin,static_attributes_basin.loc[basin]['name']))

    pngbase      = 'map_'
    pngbase      = str(Path( outfolder / pngbase ))
    usetex       = False
    outtype      = 'png'

    pngfiles = []

elif not(using_lstm is None):

    using_lstms = [ vv.split('/')[-3].split('using_')[1] for vv in validation_results ]    # ['conus-zhi-v1']
    print('Number of "using_lstms" results found: {}'.format(len(using_lstms)))

    results = {}
    for ivalidation_result, validation_result in enumerate(validation_results):

        results[using_lstms[ivalidation_result]] = xr.open_dataset(validation_result)

    pdffile      = 'timeseries_'
    usetex       = False
    outtype      = 'pdf'

else:
    raise ValueError('Not sure how this ended up here.')


# one plot per result file

# -------------------------------------------------------------------------
# Customize plots
#

if (pdffile == '') and (pngbase == ''):
    outtype = 'x'

# Main plot
if not( experiment is None):
    nrow        = 1           # # of rows of subplots per figure
    ncol        = 1           # # of columns of subplots per figure
elif not(using_lstm is None):
    nrow        = 5           # # of rows of subplots per figure
    ncol        = 1           # # of columns of subplots per figure
    if len(periods) > nrow:
        raise ValueError('Not enough rows in plot for number of periods specified (nperiods={})'.format(len(periods)))
else:
    raise ValueError('Not sure how this ended up here.')
hspace      = 0.02         # x-space between subplots
vspace      = 0.01        # y-space between subplots
right       = 0.9         # right space on page
textsize    = 14           # standard text size
dxabc       = 0.3         # % of (max-min) shift to the right from left y-axis for a,b,c,... labels
# dyabc       = -13       # % of (max-min) shift up from lower x-axis for a,b,c,... labels
dyabc       = 2.0         # % of (max-min) shift up from lower x-axis for a,b,c,... labels
dxsig       = 0.01        # % of (max-min) shift to the right from left y-axis for signature
dysig       = 0.01       # % of (max-min) shift up from lower x-axis for signature
dxtit       = 0           # % of (max-min) shift to the right from left y-axis for title
dytit       = 1.3         # % of (max-min) shift up from lower x-axis for title

lwidth      = 0.75         # linewidth
elwidth     = 1.0         # errorbar line width
alwidth     = 1.0         # axis line width
glwidth     = 0.5         # grid line width
msize       = 3.0         # marker size
mwidth      = 1.0         # marker edge width
mcol1       = '0.0'       # primary marker colour
mcol2       = '0.4'                     # secondary
mcol3       = '0.0' # third
mcols       = ['0.0', '0.4', '0.4', '0.7', '0.7', '1.0']
lcol1       = color.colours('blue')   # primary line colour
lcol2       = '0.0'
lcol3       = '0.0'
lcols       = ['None', 'None', 'None', 'None', 'None', '0.0']
hatches     = [None, None, None, None, None, '//']

# Legend
llxbbox     = 0.5          # x-anchor legend bounding box
llybbox     = 0.95         # y-anchor legend bounding box
llrspace    = 0.          # spacing between rows in legend
llcspace    = 1.0         # spacing between columns in legend
llhtextpad  = 0.4         # the pad between the legend handle and text
llhlength   = 1.5         # the length of the legend handles
frameon     = False       # if True, draw a frame around the legend. If None, use rc

# PNG
dpi         = 300         # 150 for testing
transparent = False
bbox_inches = 'tight'
pad_inches  = 0.035

# Clock options
ymax = 0.6
ntextsize   = 'medium'       # normal textsize
# modules
bmod        = 0.5            # fraction of ymax from center to start module colours
alphamod    = 0.7            # alpha channel for modules
fwm         = 0.05           # module width to remove at sides
ylabel1     = 1.15           # position of module names
ylabel2     = 1.35           # position of class names
mtextsize   = 'large'        # 1.3*textsize # textsize of module labels
# bars
bpar        = 0.4            # fraction of ymax from center to start with parameter bars
fwb         = [0.7,0.4,0.3]  # width of bars
plwidth     = 0.5
# parameters in centre
bplabel     = 0.1            # fractional distance of ymax of param numbers in centre from 0-line
ptextsize   = 'medium'       # 'small' # 0.8*textsize # textsize of param numbers in centre
# yaxis
space4yaxis = 2              # space for y-axis (integer)
ytextsize   = 'medium'       # 'small' # 0.8*textsize # textsize of y-axis
sig         = 'J Mai' # sign the plot

import matplotlib as mpl
from matplotlib.patches import Rectangle, Circle, Polygon
from mpl_toolkits.basemap import Basemap


# colors
if dobw:
    c = np.linspace(0.2, 0.85, nmod)
    c = np.ones(nmod)*0.7
    c = [ str(i) for i in c ]
    ocean_color = '0.1'
else:
    # c = [(165./255.,  0./255., 38./255.), # interception
    #      (215./255., 48./255., 39./255.), # snow
    #      (244./255.,109./255., 67./255.), # soil moisture
    #      (244./255.,109./255., 67./255.), # soil moisture
    #      (253./255.,174./255., 97./255.), # direct runoff
    #      (254./255.,224./255.,144./255.), # Evapotranspiration
    #      (171./255.,217./255.,233./255.), # interflow
    #      (116./255.,173./255.,209./255.), # percolation
    #      ( 69./255.,117./255.,180./255.), # routing
    #      ( 49./255., 54./255.,149./255.)] # geology
    c = get_brewer('rdylbu11', rgb=True)
    tmp = c.pop(5)   # rm yellow

    # use a colormap from Brewer module
    c         = color.get_brewer('gsdtol', rgb=True)[2:]
    cmap_gray = mpl.colors.ListedColormap(c)

    #c.insert(2,c[2]) # same colour for both soil moistures
    ocean_color = (151/256., 183/256., 224/256.)

    cc = color.get_brewer('dark_rainbow_256', rgb=True)
    cc = cc[::-1] # reverse colors
    cmap = mpl.colors.ListedColormap(cc)

    if not( experiment is None):
        # green-pink colors
        cc = color.get_brewer('piyg10', rgb=True)
        cmap = mpl.colors.ListedColormap(cc)
    elif not(using_lstm is None):
        # paired-colors
        if len(using_lstms) <= 3:
            cc = color.get_brewer('paired3', rgb=True)
        elif len(using_lstms) <= 12:
            cc = color.get_brewer('paired'+str(len(using_lstms)), rgb=True)
        else:
            raise ValueError('There are so many models that a new color palette is needed.')
        cmap = mpl.colors.ListedColormap(cc)

# -------------------------------------------------------------------------
# Plot
#

if not( experiment is None):

    # -------------------------------------------------------------------------
    # MAP: Results of experiment
    #
    outtype = 'png'

    if (outtype == 'pdf'):
        mpl.use('PDF') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        # Customize: http://matplotlib.sourceforge.net/users/customizing.html
        mpl.rc('ps', papersize='a4', usedistiller='xpdf') # ps2pdf
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
    elif (outtype == 'png'):
        mpl.use('Agg') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
        mpl.rc('savefig', dpi=dpi, format='png')
    else:
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(4./5.*8.27,4./5.*11.69)) # a4 portrait
    mpl.rc('font', size=textsize)
    mpl.rc('lines', linewidth=lwidth, color='black')
    mpl.rc('axes', linewidth=alwidth, labelcolor='black')
    mpl.rc('path', simplify=False) # do not remove


    if (outtype == 'pdf'):
        print('Plot PDF ', pdffile)
        pdf_pages = PdfPages(pdffile)
    elif (outtype == 'png'):
        print('Plot PNG ', pngbase)
    else:
        print('Plot X')
    # figsize = mpl.rcParams['figure.figsize']

    ifig = 0

    for result in list(dict_results.keys()):

        ifig += 1
        iplot = 0
        print('Plot - Fig ', ifig)
        fig = plt.figure(ifig)

        iplot += 1
        pos_plot = position(nrow,ncol,iplot,hspace=hspace,vspace=vspace)
        sub = fig.add_axes(pos_plot) #, facecolor='none')

        lat_1     =   (llcrnrlat+urcrnrlat)/2  # first  "equator"
        lat_2     =   (llcrnrlat+urcrnrlat)/2  # second "equator"
        lat_0     =   (llcrnrlat+urcrnrlat)/2  # center of the map
        lon_0     =   (llcrnrlon+urcrnrlon)/2  # center of the map

        m = Basemap(projection='lcc', area_thresh=2000.,
                    llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
                    lat_1=lat_1, lat_2=lat_2, lat_0=lat_0, lon_0=lon_0,
                    resolution='i') # Lambert conformal


        # draw parallels and meridians.
        # labels: [left, right, top, bottom]
        m.drawparallels(parallels,labels=[1,0,1,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(meridians,labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')

        # draw cooastlines and countries
        m.drawcoastlines(linewidth=0.3)
        m.drawmapboundary(fill_color=ocean_color, linewidth=0.3)
        m.drawcountries(color='black', linewidth=0.3)
        m.drawstates(color='gray', linewidth=0.3)
        m.fillcontinents(color='white', lake_color=ocean_color)

        # Gauges
        gauges_w_kge = 0
        gauges_wo_kge = 0
        gauges_not_enough_obs = 0
        kges = []

        try:
            station_list = np.array([ ii.encode('ascii') for ii in df['Q']['station_id'].data ])
        except:
            station_list = np.array([ ii for ii in df['Q']['station_id'].data ])
        for gauge in list(gauge_dict.keys()):

            # number of available observations
            if 'cal' in result.split('.')[-1]:
                nobs = int(df['Q'][np.where(station_list==gauge.encode('ascii'))[0][0]].sel(time=slice("2000-01-01", "2018-12-31")).count().data)
            elif 'valtemp' in result.split('.')[-1]:
                nobs = int(df['Q'][np.where(station_list==gauge.encode('ascii'))[0][0]].sel(time=slice("1980-01-01", "1999-12-31")).count().data)
            else:
                raise ValueError('Dont know how to count number of observations available for this experiment')

            if (nobs > 3*365):

                # color based on KGE of that basin
                icolor = 'red'
                ikge = gauge_dict[gauge]['metrics'][result]['KGE_1D']
                inse = gauge_dict[gauge]['metrics'][result]['NSE_1D']

                min_kge = 0.0
                max_kge = 1.0
                scale   = 'linear'

                if not( np.isnan(ikge) ):
                    if ikge <= min_kge:
                        icolor = cc[0]
                    elif ikge > max_kge:
                        icolor = cc[-1]
                    else:
                        if scale == 'linear':
                            # linear scale
                            icolor = cc[int((ikge-min_kge)/(max_kge-min_kge)*(len(cc)-1))+1]
                        elif scale == 'log':
                            # logarithmic scale
                            icolor = cc[np.where(ikge > cticks_log)[0][-1]]
                        else:
                            raise ValueError('Scale "{}" method not implemented!'.format(scale))

                    xpt = m(gauge_dict[gauge]["lon"],gauge_dict[gauge]["lat"])[0]
                    ypt = m(gauge_dict[gauge]["lon"],gauge_dict[gauge]["lat"])[1]
                    sub.plot(xpt, ypt,
                             linestyle='None', marker='o', markeredgecolor=icolor, markerfacecolor=icolor,
                             markersize=msize, markeredgewidth=0.0)

                    if ikge < 0.0:
                        print("Gauge {} (lat={:8.4f},lon={:8.4f}) has very low KGE value: {:8.3f} (nobs={})".format(gauge,gauge_dict[gauge]["lat"],gauge_dict[gauge]["lon"],ikge,nobs))

                    gauges_w_kge += 1
                    kges = np.append(kges, ikge)
                else:
                    gauges_not_enough_obs += 1
            else:
                gauges_wo_kge += 1

        if dosig:
            from signature2plot import signature2plot
            signature2plot(sub, dxsig, dysig, sig, transform=sub.transAxes,
                       horizontalalignment='left',
                       color='gray',
                       italic=True, small=True, mathrm=True, usetex=usetex)

        # median
        print('median KGE = {} ({}, {}) based on {} basins'.format(np.median(kges),np.percentile(kges,5),np.percentile(kges,95),len(kges)))

        # add nbasins
        sub.text(0.99,0.99,str2tex('$n_{basins} = '+str(len(kges))+'$',usetex=usetex),
                         verticalalignment='top',horizontalalignment='right',
                         fontsize=textsize,transform=sub.transAxes)

        # add ABC
        if doabc:
            sub.text(0.0,1.0,str2tex(chr(64+iplot),usetex=usetex),
                         verticalalignment='bottom',horizontalalignment='left',
                         fontweight='bold',
                         fontsize=textsize+4,transform=sub.transAxes)

        # add title
        sub.text(0.5,1.0,str2tex(experiment+' - '+result,usetex=usetex),
                         verticalalignment='bottom',horizontalalignment='center',
                         fontweight='bold',
                         fontsize=textsize,transform=sub.transAxes)

        # -------------------------------------------------------------------------
        # Colorbar - vertical
        # -------------------------------------------------------------------------
        #     [left, bottom, width, height]
        # pos cbar:  [0.125  0.772  0.5375 0.128 ]
        # pos cbar:  [0.3625 0.772  0.5375 0.128 ]
        # pos cbar:  [0.125  0.604  0.5375 0.128 ]
        # pos cbar:  [0.3625 0.604  0.5375 0.128 ]
        # pos cbar:  [0.125  0.436  0.5375 0.128 ]

        if case_study == 'conus-zhi':
            extra_shift = -0.2
        elif case_study == 'camels-us-newman':
            extra_shift = -0.2
        elif case_study == 'grip-gl-mai':
            extra_shift = -0.15
        else:
            extra_shift = -0.0

        print("pos plot: ",position(nrow,ncol,iplot,hspace=hspace,vspace=vspace))
        pos_cbar = pos_plot + [0.00,-0.01-extra_shift,-0.0,-pos_plot[3]+0.01]
        print("pos cbar: ",pos_cbar)

        csub_cal    = fig.add_axes( pos_cbar )

        if scale == 'linear':
            # linear scale
            cbar = mpl.colorbar.ColorbarBase(csub_cal, norm=mpl.colors.Normalize(vmin=min_kge, vmax=max_kge), cmap=cmap, orientation='horizontal', extend='min')
        elif scale == 'log':
            # logarithmic scale
            cbar = mpl.colorbar.ColorbarBase(csub_cal, norm=mpl.colors.LogNorm(vmin=min_kge, vmax=max_kge), cmap=cmap, orientation='horizontal', extend='min')
        else:
            raise ValueError('Scale "{}" method not implemented!'.format(scale))

        cbar.set_label(str2tex('Kling-Gupta Efficiency [-]',usetex=usetex))


        if (outtype == 'pdf'):
            pdf_pages.savefig(fig)
            plt.close(fig)
        elif (outtype == 'png'):
            pngfile = pngbase+"{}".format(result)+".png"
            pngfiles.append( pngfile )
            fig.savefig(pngfile, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches)
            plt.close(fig)


    # -------------------------------------------------------------------------
    # Finished
    #

    if (outtype == 'pdf'):
        pdf_pages.close()
    elif (outtype == 'png'):
        pass
    else:
        plt.show()

    t2    = time.time()
    strin = '[m]: '+astr((t2-t1)/60.,1) if (t2-t1)>60. else '[s]: '+astr(t2-t1,0)
    print('Time ', strin)

    if (outtype == 'pdf'):
        print('Wrote: {}'.format(pdffile))
    elif (outtype == 'png'):
        print('Wrote: {}'.format(pngfiles))



elif not(using_lstm is None):

    # -------------------------------------------------------------------------
    # TIMESERIES: Results of validation experiment(s)
    #
    outtype = 'pdf'

    if (outtype == 'pdf'):
        mpl.use('PDF') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        # Customize: http://matplotlib.sourceforge.net/users/customizing.html
        mpl.rc('ps', papersize='a4', usedistiller='xpdf') # ps2pdf
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
    elif (outtype == 'png'):
        mpl.use('Agg') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
        mpl.rc('savefig', dpi=dpi, format='png')
    else:
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(4./5.*8.27,4./5.*11.69)) # a4 portrait
    mpl.rc('font', size=textsize)
    mpl.rc('lines', linewidth=lwidth, color='black')
    mpl.rc('axes', linewidth=alwidth, labelcolor='black')
    mpl.rc('path', simplify=False) # do not remove

    ifig = 0

    outfolder = Path(dir_path+"/../regions/"+case_study+"/predictions/plots/")
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    pdffile      = 'timeseries.pdf'
    pdffile      = str(Path( outfolder / pdffile ))
    usetex       = False

    if (outtype == 'pdf'):
        print('Plot PDF ', pdffile)
        pdf_pages = PdfPages(pdffile)
    elif (outtype == 'png'):
        print('Plot PNG ', pngbase)
    else:
        print('Plot X')
    # figsize = mpl.rcParams['figure.figsize']

    nodata = -9999.

    basins = results[using_lstms[0]]['basin'].data # assuming all have same basins
    print('Number of basins found:                {}'.format(len(basins)))
    kges = { uu: { bb: { period['string']: nodata for period in periods } for bb in basins } for uu in using_lstms }
    for ibasin, basin in enumerate(basins[0:3]):

        ifig += 1
        iplot = 0
        print('Plot - Fig ', ifig)
        fig = plt.figure(ifig)

        for iperiod,period in enumerate(periods):

            iplot += 1
            #     [left, bottom, width, height]
            pos_plot = position(nrow,ncol,iplot,hspace=hspace,vspace=vspace) + [0,-0.03*iperiod,0,0]
            sub = fig.add_axes(pos_plot) #, facecolor='none')

            for iusing_lstm,using_lstm in enumerate(using_lstms):

                # get data only for current period
                data_for_period = results[using_lstm].sel(datetime=slice(period['start'], period['end']))

                idx_basin = np.where(data_for_period['basin'].data == basin)[0][0]
                date = data_for_period['datetime']

                # simulation
                data_sim = data_for_period['qobs_m3_per_s_sim'][idx_basin].data

                # observation
                data_obs = data_for_period['qobs_m3_per_s_obs'][idx_basin].data

                # derive KGE
                if not( np.all(np.isnan(data_obs)) ):
                    idx_time = ~( np.isnan(data_obs) | np.isnan(data_sim) )
                    if (len(idx_time) > 3*365):   # at least 3 years of observations
                        ikge = kge(data_obs[idx_time], data_sim[idx_time])
                        kges[using_lstm][basin][period['string']] = ikge
                else:
                    print('No observation found for basin {} in LSTM model {} in period {}'.format(basin,using_lstm,period['string']))

                # plot observation (one time only)
                if iusing_lstm == 0:
                    if not( np.all(np.isnan(data_obs)) ):
                        sub.plot(date, data_obs,
                             color='0.7',
                             linewidth=0.0,
                             marker='o',
                             markersize=msize/1,
                             markeredgewidth=msize/4,
                             markerfacecolor='w',
                             label='observation', alpha=0.5)

                # plot simulation
                if not( np.all(np.isnan(data_sim)) ):
                    icolor = iusing_lstm
                    if (kges[using_lstm][basin][period['string']] != nodata ):
                        label = "{} (KGE={:.2f})".format(using_lstm,kges[using_lstm][basin][period['string']])
                    else:
                        label = "{}".format(using_lstm)
                    sub.plot(date, data_sim,
                                 color=cc[icolor],
                                 linewidth=lwidth,
                                 label=label, alpha=0.5)
                else:
                    print('No simulation data found for basin {} in LSTM model {}'.format(basin,using_lstm))

            # set axis labels
            if iplot == len(periods):
                sub.set_xlabel(str2tex('simulation time', usetex=usetex))
            sub.set_ylabel(str2tex('Q [m$^3$ s$^{-1}$]', usetex=usetex))

            # add title
            if iplot == 1:
                sub.text(0.5,1.0,str2tex(basin,usetex=usetex),
                         verticalalignment='bottom',horizontalalignment='center',
                         fontweight='bold',
                         fontsize=textsize,transform=sub.transAxes)

            # add legend
            ll = plt.legend(frameon=frameon, ncol=2, bbox_to_anchor=(llxbbox,llybbox), loc='upper center',
                           scatterpoints=1, numpoints=1,
                           fontsize=textsize-4,
                           labelspacing=llrspace, columnspacing=llcspace, handletextpad=llhtextpad, handlelength=llhlength)
            plt.setp(ll.get_texts(), fontsize='small')



        if (outtype == 'pdf'):
            pdf_pages.savefig(fig)
            plt.close(fig)
        elif (outtype == 'png'):
            pngfile = pngbase+"{}".format(using_lstm)+".png"
            pngfiles.append( pngfile )
            fig.savefig(pngfile, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches)
            plt.close(fig)


    # -------------------------------------------------------------------------
    # Finished
    #

    if (outtype == 'pdf'):
        pdf_pages.close()
    elif (outtype == 'png'):
        pass
    else:
        plt.show()

    t2    = time.time()
    strin = '[m]: '+astr((t2-t1)/60.,1) if (t2-t1)>60. else '[s]: '+astr(t2-t1,0)
    print('Time ', strin)

    if (outtype == 'pdf'):
        print('Wrote: {}'.format(pdffile))
    elif (outtype == 'png'):
        print('Wrote: {}'.format(pngfiles))


    # write summary to .txt
    filename = '.'.join(pdffile.split('.')[0:-1])+'.txt'
    ff = open(filename, "w")

    print('')
    print('summary statistics:')
    for using_lstm in using_lstms:

        for iperiod,period in enumerate(periods):

            kges_lstm = np.array([ kges[using_lstm][bb][period['string']] for bb in basins if ((kges[using_lstm][bb][period['string']] != nodata) and (not(np.isnan(kges[using_lstm][bb][period['string']]))))])
            if len(kges_lstm > 0):
                summary_string = '   {:20s}: {}: median KGE = {} ({}, {}) based on {} basins'.format(
                    using_lstm,
                    period['string'],
                    np.nanmedian(kges_lstm),
                    np.nanpercentile(kges_lstm,5),
                    np.nanpercentile(kges_lstm,95),
                    len(kges_lstm))
            else:
                summary_string = '   {:20s}: {}: no KGE results since no basin had observations (?!)'.format(
                    using_lstm,
                    period['string'])
            print(summary_string)
            ff.write(summary_string+'\n')

    ff.close()
    print('Wrote: {}'.format(filename))

    # write all KGE results to .json
    filename = '.'.join(pdffile.split('.')[0:-1])+'.json'
    with open(filename, "w") as outfile:
        json.dump(kges, outfile)

    print('Wrote: {}'.format(filename))
    print('')


    # ----------------------------------------------------
    # plot map of results
    # ----------------------------------------------------

    pdffile      = 'map.pdf'
    pdffile      = str(Path( outfolder / pdffile ))
    pngbase      = '.'.join(pdffile.split('.')[0:-1])+'_'
    usetex       = False
    outtype      = 'png'


    if (outtype == 'pdf'):
        mpl.use('PDF') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        # Customize: http://matplotlib.sourceforge.net/users/customizing.html
        mpl.rc('ps', papersize='a4', usedistiller='xpdf') # ps2pdf
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
    elif (outtype == 'png'):
        mpl.use('Agg') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
        mpl.rc('savefig', dpi=dpi, format='png')
    else:
        import matplotlib.pyplot as plt
        mpl.rc('figure', figsize=(4./5.*8.27,4./5.*11.69)) # a4 portrait
    mpl.rc('font', size=textsize)
    mpl.rc('lines', linewidth=lwidth, color='black')
    mpl.rc('axes', linewidth=alwidth, labelcolor='black')
    mpl.rc('path', simplify=False) # do not remove


    pngfiles = []

    ncol  = len(periods)           # # of columns of subplots per figure
    nrow  = 1

    # green-pink colors
    cc = color.get_brewer('piyg10', rgb=True)
    cmap = mpl.colors.ListedColormap(cc)

    if (outtype == 'pdf'):
        print('Plot PDF ', pdffile)
        pdf_pages = PdfPages(pdffile)
    elif (outtype == 'png'):
        print('Plot PNG ', pngbase)
    else:
        print('Plot X')
    # figsize = mpl.rcParams['figure.figsize']

    ifig = 0

    for using_lstm in list(kges.keys()):

        ifig += 1
        iplot = 0
        print('Plot - Fig {} - using_lstm = {}'.format(ifig,using_lstm))
        fig = plt.figure(ifig)

        for iperiod,period in enumerate(periods):

            iplot += 1
            pos_plot = position(nrow,ncol,iplot,hspace=hspace,vspace=vspace)
            sub = fig.add_axes(pos_plot) #, facecolor='none')

            lat_1     =   (llcrnrlat+urcrnrlat)/2  # first  "equator"
            lat_2     =   (llcrnrlat+urcrnrlat)/2  # second "equator"
            lat_0     =   (llcrnrlat+urcrnrlat)/2  # center of the map
            lon_0     =   (llcrnrlon+urcrnrlon)/2  # center of the map

            m = Basemap(projection='lcc', area_thresh=2000.,
                        llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
                        lat_1=lat_1, lat_2=lat_2, lat_0=lat_0, lon_0=lon_0,
                        resolution='i') # Lambert conformal


            # draw parallels and meridians.
            # labels: [left, right, top, bottom]
            if iplot == 1:
                m.drawparallels(parallels,labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5', fontsize=textsize-2)
            elif iplot == len(periods):
                m.drawparallels(parallels,labels=[0,1,0,0], dashes=[1,1], linewidth=0.25, color='0.5', fontsize=textsize-2)
            else:
                 m.drawparallels(parallels,labels=[0,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5', fontsize=textsize-2)
            m.drawmeridians(meridians,labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5', fontsize=textsize-2)

            # draw cooastlines and countries
            m.drawcoastlines(linewidth=0.3)
            m.drawmapboundary(fill_color='white', linewidth=0.3) # ocean_color
            m.drawcountries(color='black', linewidth=0.3)
            m.drawstates(color='gray', linewidth=0.3)
            m.fillcontinents(color='0.95', lake_color='white')  # ocean_color

            # Gauges
            station_w_kge = 0
            station_wo_kge = 0
            ikges = []

            # read basins.csv for (lat,lon,obs_q)
            static_attributes_basin   = pd.read_csv(project_root / '_'.join(using_lstm.split('_')[0:-1]) / 'basins.csv', index_col=[0],
                                                    dtype={'id': 'str', 'name': 'str', 'lat': 'float', 'lon': 'float', 'obs_q': 'str'})
            qobs_location = { static_attributes_basin.loc[bb]['obs_q']:
                                  { 'lat': static_attributes_basin.loc[bb]['lat'],
                                    'lon': static_attributes_basin.loc[bb]['lon'] }
                                  for bb in list(static_attributes_basin.index) }
            station_list = list(kges[using_lstm].keys())

            # check that all basins are found
            for bb in list(qobs_location.keys()):
                if not( bb in station_list):
                    raise ValueError('Basin {} not found in station_list results of LSTM {}'.format(bb,using_lstm))

            for station in list(station_list):

                # color based on KGE of that basin
                icolor = 'red'
                ikge = kges[using_lstm][station][period['string']]

                min_kge = 0.0
                max_kge = 1.0
                scale   = 'linear'

                if not( np.isnan(ikge) ) and not(ikge == nodata):
                    if ikge <= min_kge:
                        icolor = cc[0]
                    elif ikge > max_kge:
                        icolor = cc[-1]
                    else:
                        if scale == 'linear':
                            # linear scale
                            icolor = cc[int((ikge-min_kge)/(max_kge-min_kge)*(len(cc)-1))+1]
                        elif scale == 'log':
                            # logarithmic scale
                            icolor = cc[np.where(ikge > cticks_log)[0][-1]]
                        else:
                            raise ValueError('Scale "{}" method not implemented!'.format(scale))

                    xpt = m(qobs_location[station]["lon"],qobs_location[station]["lat"])[0]
                    ypt = m(qobs_location[station]["lon"],qobs_location[station]["lat"])[1]
                    sub.plot(xpt, ypt,
                             linestyle='None', marker='o', markeredgecolor=icolor, markerfacecolor=icolor,
                             markersize=msize, markeredgewidth=0.0)

                    if ikge < 0.0:
                        print("   >>> Gauge {} (lat={:8.4f},lon={:8.4f}) has very low KGE value: {:8.3f}".format(
                            station,qobs_location[station]["lat"],qobs_location[station]["lon"],ikge))

                    station_w_kge += 1
                    ikges = np.append(ikges, ikge)
                else:
                    station_wo_kge += 1


            if dosig:
                from signature2plot import signature2plot
                signature2plot(sub, dxsig, dysig, sig, transform=sub.transAxes,
                           horizontalalignment='left',
                           color='gray',
                           italic=True, small=True, mathrm=True, usetex=usetex)

            # median
            print('   {:20s}: {}: median KGE = {} ({}, {}) based on {} basins'.format(
                using_lstm, period['string'],
                np.median(ikges),np.percentile(ikges,5),np.percentile(ikges,95),len(ikges)))

            # add nbasins
            sub.text(0.99,0.99,str2tex('$n_{basins} = '+str(len(ikges))+'$',usetex=usetex),
                             verticalalignment='top',horizontalalignment='right',
                             fontsize=textsize-2,transform=sub.transAxes)

            # add case_study / model
            if iplot == len(periods):
                sub.text(1.0,1.1,str2tex('region: '+case_study+'\n'+'model: '+using_lstm+'\n',usetex=usetex),
                             verticalalignment='bottom',horizontalalignment='right',
                             fontsize=textsize-2, color='0.5',transform=sub.transAxes)

            # add ABC
            if doabc:
                sub.text(0.0,1.0,str2tex(chr(64+iplot),usetex=usetex),
                             verticalalignment='bottom',horizontalalignment='left',
                             fontweight='bold',
                             fontsize=textsize+4,transform=sub.transAxes)

            # add title
            sub.text(0.5,1.0,str2tex(period['string'].replace(':',' to '),usetex=usetex),
                             verticalalignment='bottom',horizontalalignment='center',
                             fontweight='bold',
                             fontsize=textsize,transform=sub.transAxes)

        if (outtype == 'pdf'):
            pdf_pages.savefig(fig)
            plt.close(fig)
        elif (outtype == 'png'):
            pngfile = pngbase+"{}".format(using_lstm)+".png"
            pngfiles.append( pngfile )
            fig.savefig(pngfile, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches)
            plt.close(fig)

    # -------------------------------------------------------------------------
    # Colorbar - vertical
    # -------------------------------------------------------------------------
    #     [left, bottom, width, height]
    # pos cbar:  [0.125  0.772  0.5375 0.128 ]
    # pos cbar:  [0.3625 0.772  0.5375 0.128 ]
    # pos cbar:  [0.125  0.604  0.5375 0.128 ]
    # pos cbar:  [0.3625 0.604  0.5375 0.128 ]
    # pos cbar:  [0.125  0.436  0.5375 0.128 ]

    ifig += 1
    iplot = 0
    print('Plot - Fig {} - legend'.format(ifig))
    fig = plt.figure(ifig)

    #print("pos plot: ",position(nrow,ncol,iplot,hspace=hspace,vspace=vspace))
    pos_cbar = [pos_plot[0],pos_plot[0],pos_plot[0],0.01]
    #print("pos cbar: ",pos_cbar)

    csub_cal    = fig.add_axes( pos_cbar )

    if scale == 'linear':
        # linear scale
        cbar = mpl.colorbar.ColorbarBase(csub_cal, norm=mpl.colors.Normalize(vmin=min_kge, vmax=max_kge), cmap=cmap, orientation='horizontal', extend='min')
    elif scale == 'log':
        # logarithmic scale
        cbar = mpl.colorbar.ColorbarBase(csub_cal, norm=mpl.colors.LogNorm(vmin=min_kge, vmax=max_kge), cmap=cmap, orientation='horizontal', extend='min')
    else:
        raise ValueError('Scale "{}" method not implemented!'.format(scale))

    cbar.set_label(str2tex('Kling-Gupta Efficiency [-]',usetex=usetex))


    if (outtype == 'pdf'):
        pdf_pages.savefig(fig)
        plt.close(fig)
    elif (outtype == 'png'):
        pngfile = pngbase+"legend.png"
        pngfiles.append( pngfile )
        fig.savefig(pngfile, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close(fig)


    # -------------------------------------------------------------------------
    # Finished
    #

    if (outtype == 'pdf'):
        pdf_pages.close()
    elif (outtype == 'png'):
        pass
    else:
        plt.show()

    t2    = time.time()
    strin = '[m]: '+astr((t2-t1)/60.,1) if (t2-t1)>60. else '[s]: '+astr(t2-t1,0)
    print('Time ', strin)

    if (outtype == 'pdf'):
        print('Wrote: {}'.format(pdffile))
    elif (outtype == 'png'):
        print('Wrote: {}'.format(pngfiles))


else:
    raise ValueError('Not sure how this ended up here.')
