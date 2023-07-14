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

# pyenv activate env-3.8.5-nrcan

# python 04_plot_basin_map.py -s Wisconsin -p map_wisconsin.pdf
# python 04_plot_basin_map.py -s Great-Lakes -p map_great-lakes.pdf
# python 04_plot_basin_map.py -s North-America -p map_north-america.pdf
# python 04_plot_basin_map.py -s GRIP-GL -p map_grip-gl.pdf

# python 04_plot_basin_map.py -s Wisconsin -g map_wisconsin
# python 04_plot_basin_map.py -s Great-Lakes -g map_great-lakes
# python 04_plot_basin_map.py -s North-America -g map_north-america
# python 04_plot_basin_map.py -s GRIP-GL -g map_grip-gl


"""

Plots maps of shapefiles.

History
-------
Written,  JM, Jun 2023

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

pngbase      = ''
pdffile      = ''
usetex       = False
case_study   = None


parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Plot basin shape.''')
parser.add_argument('-g', '--pngbase', action='store',
                    default=pngbase, dest='pngbase', metavar='pngbase',
                    help='Name basis for png output files (default: open screen window).')
parser.add_argument('-p', '--pdffile', action='store',
                    default=pdffile, dest='pdffile', metavar='pdffile',
                    help='Name of pdf output file (default: open screen window).')
parser.add_argument('-t', '--usetex', action='store_true', default=usetex, dest="usetex",
                    help="Use LaTeX to render text in pdf.")
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. E.g. 'Wisconsin', 'Great-Lakes', 'North-America'.")

args         = parser.parse_args()
pngbase      = args.pngbase
pdffile      = args.pdffile
usetex       = args.usetex
case_study   = args.case_study

if case_study is None:
    raise ValueError("Case study (-s) must be specified!")

if (pdffile != '') & (pngbase != ''):
    print('\nError: PDF and PNG are mutually exclusive. Only either -p or -g possible.\n')
    parser.print_usage()
    import sys
    sys.exit()

del parser, args

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/lib')

import color                            # in lib/
from position      import position      # in lib/
from abc2plot      import abc2plot      # in lib/
from brewer        import get_brewer    # in lib/
from autostring    import astr          # in lib/
from str2tex       import str2tex       # in lib/
from fread         import fread         # in lib/

import fiona          # some shapefile coordinate stuff
import numpy as np
import xarray as xr
import pandas as pd
import copy                       # deep copy objects, arrays etc
import time
import os
import shapefile
import glob
from   osgeo                import ogr
from   matplotlib.patches   import Polygon, Ellipse
from   mpl_toolkits.basemap import Basemap
t1 = time.time()


if case_study == 'Wisconsin':
    project_root = dir_path+'/../regions/Wisconsin_waterheds/shapefiles/'
    shpfile = glob.glob( project_root+'/*/*_lp.shp')

    llcrnrlon =  -93.0
    urcrnrlon =  -86.1
    llcrnrlat =   42.0
    urcrnrlat =   47.2

elif case_study == 'Great-Lakes':
    project_root = dir_path+'/../regions/Great_Lakes_watersheds/shapefiles/'
    shpfile = glob.glob( project_root+'/*/*_lp.shp')

    llcrnrlon =  -91.0
    urcrnrlon =  -73.0
    llcrnrlat =   40.5
    urcrnrlat =   49.8

elif case_study == 'North-America':
    project_root = dir_path+'/../regions/North_America_watersheds/shapefiles/'
    shpfile = glob.glob( project_root+'/*/*_lp.shp')

    llcrnrlon =  -125.0
    urcrnrlon =  -70.0
    llcrnrlat =   23.5
    urcrnrlat =   49.5

elif case_study == 'GRIP-GL':
    project_root = dir_path+'/../regions/GRIP-GL/shapefiles/'
    shpfile = glob.glob( project_root+'/*/*_lp.shp')

    llcrnrlon =  -93.0
    urcrnrlon =  -72.0
    llcrnrlat =   39.0
    urcrnrlat =   51.0

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))

catchfile_shp = [ '.'.join(ss.split('.')[0:-1]) for ss in shpfile ]
print("Found {} shapefiles.".format(len(catchfile_shp)))

# -------------------------------------------------------------------------
# Customize plots
#

if (pdffile == ''):
    if (pngbase == ''):
        outtype = 'x'
    else:
        outtype = 'png'
        pngbase = project_root+pngbase
else:
    outtype = 'pdf'
    pdffile = project_root+pdffile

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
# Fig 2: Domain of Great Lakes and gauge stations
#
ifig += 1
iplot = 0
print('Plot - Fig ', ifig)
fig = plt.figure(ifig)

iplot += 1
sub = fig.add_axes(position(nrow,ncol,iplot,hspace=hspace,vspace=vspace)) #, facecolor='none')

lat_1     =   (llcrnrlat+urcrnrlat)/2  # first  "equator"
lat_2     =   (llcrnrlat+urcrnrlat)/2  # second "equator"
lat_0     =   (llcrnrlat+urcrnrlat)/2  # center of the map
lon_0     =   (llcrnrlon+urcrnrlon)/2  # center of the map

m = Basemap(projection='lcc', area_thresh=2000.,
            llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
            lat_1=lat_1, lat_2=lat_2, lat_0=lat_0, lon_0=lon_0,
            resolution='i') # Lambert conformal

coord_catch = []
for ishape in range(len(catchfile_shp)):
    with fiona.open(catchfile_shp[ishape]+'.shp') as src:
        for ii in range(len(src)):
            coord_catch.append(src[ii]['geometry']['coordinates'])


# draw parallels and meridians.
# labels: [left, right, top, bottom]
if case_study == 'Wisconsin':
    m.drawparallels(np.arange( -80., 81., 2.),labels=[1,0,1,0], dashes=[1,1], linewidth=0.25, color='0.5')
    m.drawmeridians(np.arange(-180.,181., 2.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
elif case_study == 'Great-Lakes':
    m.drawparallels(np.arange( -80., 81., 3.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
    m.drawmeridians(np.arange(-180.,181., 5.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
elif case_study == 'North-America':
    m.drawparallels(np.arange( -80., 81., 5.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
    m.drawmeridians(np.arange(-180.,181.,10.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
elif case_study == 'GRIP-GL':
    m.drawparallels(np.arange( -80., 81., 3.),labels=[1,0,0,0], dashes=[1,1], linewidth=0.25, color='0.5')
    m.drawmeridians(np.arange(-180.,181., 5.),labels=[0,0,0,1], dashes=[1,1], linewidth=0.25, color='0.5')
else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))

# draw cooastlines and countries
m.drawcoastlines(linewidth=0.3)
m.drawmapboundary(fill_color=ocean_color, linewidth=0.3)
m.drawcountries(color='black', linewidth=0.3)
m.drawstates(color='gray', linewidth=0.3)
m.fillcontinents(color='white', lake_color=ocean_color)

# allcnames = [ shortname[i] for i in range(ncatchfile_shp) ]
# if usetex:
#     allcnames = [ r'$\mathbf{'+i+'}$' for i in allcnames ]

# Catchments
nshapes = len(coord_catch)
min_lon = 99999.
max_lon = -99999.
min_lat = 99999.
max_lat = -99999.
for ishape in range(nshapes):
    try:
        xy = np.array(coord_catch[ishape])
    except:
        longest = np.argmax([ len(ipoly) for ipoly in coord_catch[ishape] ])
        xy = np.array(coord_catch[ishape][longest])

    #print("{}: shape xy = {}".format(ishape,np.shape(xy)))
    if len(np.shape(xy)) == 3:
        xy = xy[0]

    # record bounding box (can be used to set map box then)
    if (np.min(xy[:,0]) < min_lon):
        min_lon = np.min(xy[:,0])
    if (np.max(xy[:,0]) > max_lon):
        max_lon = np.max(xy[:,0])
    if (np.min(xy[:,1]) < min_lat):
        min_lat = np.min(xy[:,1])
    if (np.max(xy[:,1]) > max_lat):
        max_lat = np.max(xy[:,1])
    # add catchment shape to plot
    sub.add_patch(Polygon([ m(ii[0],ii[1]) for ii in xy ], facecolor=c[20], edgecolor='none', alpha=0.5))

print('lon: {} to {}'.format(min_lon,max_lon))
print('lat: {} to {}'.format(min_lat,max_lat))

# # legend
# ll = plt.legend(frameon=frameon, ncol=1, bbox_to_anchor=(llxbbox,llybbox), loc='lower center',
#                scatterpoints=1, numpoints=1,
#                labelspacing=llrspace, columnspacing=llcspace, handletextpad=llhtextpad, handlelength=llhlength)
# plt.setp(ll.get_texts(), fontsize='small')

if dosig:
    from signature2plot import signature2plot
    signature2plot(sub, dxsig, dysig, sig, transform=sub.transAxes,
               horizontalalignment='left',
               color='gray',
               italic=True, small=True, mathrm=True, usetex=usetex)

# add nbasins
sub.text(0.99,0.99,str2tex('$n_{basins} = '+str(len(catchfile_shp))+'$',usetex=usetex),
                 verticalalignment='top',horizontalalignment='right',
                 fontsize=textsize,transform=sub.transAxes)

# add ABC
if doabc:
    sub.text(0.0,1.0,str2tex(chr(64+iplot),usetex=usetex),
                 verticalalignment='bottom',horizontalalignment='left',
                 fontweight='bold',
                 fontsize=textsize+4,transform=sub.transAxes)

# add title
if case_study == 'GRIP-GL':
    sub.text(0.5,1.0,str2tex(case_study,usetex=usetex),
                 verticalalignment='bottom',horizontalalignment='center',
                 fontweight='bold',
                 fontsize=textsize,transform=sub.transAxes)
else:
    sub.text(0.5,1.0,str2tex(case_study.replace('-',' ').title(),usetex=usetex),
                 verticalalignment='bottom',horizontalalignment='center',
                 fontweight='bold',
                 fontsize=textsize,transform=sub.transAxes)


if (outtype == 'pdf'):
    pdf_pages.savefig(fig)
    plt.close(fig)
elif (outtype == 'png'):
    pngfile = pngbase+".png"
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
    print('Wrote: {}'.format(pngfile))
