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

# python 15_plot_results_final-training.py -s 'conus-zhi' -x 'conus-zhi-v1'
# python 15_plot_results_final-training.py -s 'grip-gl-mai' -x 'grip-gl-mai-v2'


"""

Plots results found in experiment onto a map.

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
dosig     = True  # True: add signature to plot
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

import pandas as pd
import xarray as xr
import numpy as np
import glob as glob
import time
import color                            # in lib/
from brewer        import get_brewer    # in lib/
from position      import position      # in lib/
from str2tex       import str2tex       # in lib/
from abc2plot      import abc2plot      # in lib/
from autostring    import astr          # in lib/

case_study   = None
experiment   = 'test'
period       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']. Default: None.")
parser.add_argument('-x', '--experiment', action='store', default=experiment, dest='experiment',
                    help="Name of LSTM experiment . Resulting files plotted are 'lstm/<experiment>/hyper-parameter-tuning/*.csv.*'. Default: 'test'.")

args         = parser.parse_args()
case_study   = args.case_study
experiment   = args.experiment

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")

del parser, args





t1 = time.time()

if case_study == 'wisconsin-lewis':
    project_root = Path(dir_path+'/../regions/wisconsin-lewis')

    llcrnrlon =  -93.0
    urcrnrlon =  -86.1
    llcrnrlat =   42.0
    urcrnrlat =   47.2

elif case_study == 'ontario-zhi':
    project_root = Path(dir_path+'/../regions/ontario-zhi')

    llcrnrlon =  -91.0
    urcrnrlon =  -73.0
    llcrnrlat =   40.5
    urcrnrlat =   49.8

elif case_study == 'conus-zhi':
    project_root = Path(dir_path+'/../regions/conus-zhi')

    llcrnrlon =  -125.0
    urcrnrlon =  -70.0
    llcrnrlat =   23.5
    urcrnrlat =   49.5

elif case_study == 'grip-gl-mai':
    project_root = Path(dir_path+'/../regions/grip-gl-mai')

    llcrnrlon =  -93.0
    urcrnrlon =  -72.0
    llcrnrlat =   39.0
    urcrnrlat =   51.0

elif case_study == 'north-america-mai':
    project_root = Path(dir_path+'/../regions/north-america-mai')

    llcrnrlon =  -116.   # lon: -131.36749999999995 to -60.98499999999996
    urcrnrlon =   -46.
    llcrnrlat =   18.    # lat: 26.920416654000064 to 59.33374999800003
    urcrnrlat =   58.

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))

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





# one plot per result file


pdffile      = ''
pngbase      = 'map_'
usetex       = False

pngfiles = []

# -------------------------------------------------------------------------
# Customize plots
#

if (pdffile == ''):
    if (pngbase == ''):
        outtype = 'x'
    else:
        outtype = 'png'
        pngbase = str(Path( outfolder / pngbase ))
else:
    outtype = 'pdf'
    pdffile = outfolder+pdffile

# Main plot
nrow        = 1           # # of rows of subplots per figure
ncol        = 1           # # of columns of subplots per figure
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

lwidth      = 1.5         # linewidth
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
llxbbox     = 0.5           # x-anchor legend bounding box
llybbox     = -0.37         # y-anchor legend bounding box
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

    # green-pink colors
    cc = color.get_brewer('piyg10', rgb=True)
    cmap = mpl.colors.ListedColormap(cc)


# -------------------------------------------------------------------------
# Plot
#

if (outtype == 'pdf'):
    print('Plot PDF ', pdffile)
    pdf_pages = PdfPages(pdffile)
elif (outtype == 'png'):
    print('Plot PNG ', pngbase)
else:
    print('Plot X')
# figsize = mpl.rcParams['figure.figsize']

ifig = 0

# -------------------------------------------------------------------------
# Fig 1: Results of experiment
#

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
    if case_study == 'wisconsin-lewis':
        m.drawparallels(np.arange( -80., 81., 2.),labels=[1,0,1,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(np.arange(-180.,181., 2.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
    elif case_study == 'ontario-zhi':
        m.drawparallels(np.arange( -80., 81., 3.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(np.arange(-180.,181., 5.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
    elif case_study == 'conus-zhi':
        m.drawparallels(np.arange( -80., 81., 5.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(np.arange(-180.,181.,10.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
    elif case_study == 'grip-gl-mai':
        m.drawparallels(np.arange( -80., 81., 3.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(np.arange(-180.,181., 5.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
    elif case_study == 'north-america-mai':
        m.drawparallels(np.arange( -80., 81., 5.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
        m.drawmeridians(np.arange(-180.,181.,10.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
    else:
        raise ValueError('Case study for {} not setup yet.'.format(case_study))

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
