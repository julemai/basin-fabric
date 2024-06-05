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


# # plot attributes (static and climate) of a region
# python 17_plot_attributes.py -s 'conus-zhi' -f 'rdrs-v2.1_north-america'


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
Written,  JM, Jun 2024

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

case_study   = None
forcing      = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Plot validation results.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']. Default: None.")
parser.add_argument('-f', '--forcing', action='store', default=forcing, dest='forcing',
                    help="Forcing type needs to be specified. E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")

args         = parser.parse_args()
case_study   = args.case_study
forcing      = args.forcing

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'camels-us-newman', 'grip-gl-mai']")
if (forcing is None):
    raise ValueError("Forcing type (-f) must be specified.E.g., one of ['rdrs-v2.1_north-america']. These files need to be available for each basin: 'regions/<case_study>/forcings/<basin>/<basin>_agg_<forcing>_lp.nc'.")

del parser, args

# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/additional_processing')



t1 = time.time()

project_root = Path(dir_path+'/../regions/'+case_study)
outfolder    = Path(dir_path+"/../regions/"+case_study+"/attributes/")

filename_attribute_static  = Path(os.path.join(outfolder,Path("static_attributes.csv")))
filename_attribute_climate = Path(os.path.join(outfolder,Path("climate_indices_"+forcing+".csv")))

filenames = [filename_attribute_static,filename_attribute_climate]



# -------------------------------------------------------------------------
# Customize plots
#
usetex = False

# Main plot
nrow        = 5           # # of rows of subplots per figure
ncol        = 6           # # of columns of subplots per figure
hspace      = 0.04         # x-space between subplots
vspace      = 0.06        # y-space between subplots
right       = 0.9         # right space on page
textsize    = 9           # standard text size
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

    # green-pink colors
    cc = color.get_brewer('piyg10', rgb=True)
    cmap = mpl.colors.ListedColormap(cc)



        

for filename in filenames:

    if not(filename.exists()):
        print("File with attributes not found:{}\nPlotting static attributes will be skipped.".format(filename))
    else:
        val_attributes = pd.read_csv(filename,dtype={'basin': str}).set_index('basin',drop=True)
        attributes = list(val_attributes.keys())

        outtype = 'pdf'
        outfile = Path(filename.parent,filename.stem+'.'+outtype )

    if (outtype == 'pdf'):

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages

        plt.close('all')
        
        mpl.use('PDF') # set directly after import matplotlib
        
        # Customize: http://matplotlib.sourceforge.net/users/customizing.html
        mpl.rc('ps', papersize='a4', usedistiller='xpdf') # ps2pdf
        #mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        mpl.rc('figure', figsize=(11.69,8.27)) # a4 landscape
        if usetex:
            mpl.rc('text', usetex=True)
        else:
            mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            #mpl.rc('font',**{'family':'serif','serif':['times']})
        mpl.rc('text.latex') #, unicode=True)
    elif (outtype == 'png'):
        mpl.use('Agg') # set directly after import matplotlib
        import matplotlib.pyplot as plt
        #mpl.rc('figure', figsize=(8.27,11.69)) # a4 portrait
        mpl.rc('figure', figsize=(11.69,8.27)) # a4 landscape
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

    pdffile      = outfile
    usetex       = False

    if (outtype == 'pdf'):
        print('Plot PDF ', pdffile)
        pdf_pages = PdfPages(pdffile)
    elif (outtype == 'png'):
        print('Plot PNG ', pngbase)
    else:
        print('Plot X')
    # figsize = mpl.rcParams['figure.figsize']


    ifig += 1
    iplot = 0
    print('Plot - Fig ', ifig)
    fig = plt.figure(ifig)


    for attribute in attributes:
        
        iplot += 1
        pos_plot = position(nrow,ncol,iplot,hspace=hspace,vspace=vspace)
        sub = fig.add_axes(pos_plot) #, facecolor='none')

        print('attribute: {:60s} (min={:8.2f}, max={:8.2f}, median={:8.2f})'.format(attribute,
                                                                     np.min(val_attributes[attribute].values),
                                                                     np.max(val_attributes[attribute].values),
                                                                     np.median(val_attributes[attribute].values)))
        
        if attribute in ['CLAY', 'GRAV', 'SAND', 'SILT']:
            sub.set_xlim(0,100)
            sub.hist(val_attributes[attribute].values,range=(0,100))
        elif attribute in ['Temperate-or-sub-polar-needleleaf-forest',
                           'Sub-polar-taiga-needleleaf-forest',
                           'Tropical-or-sub-tropical-broadleaf-evergreen-forest',
                           'Tropical-or-sub-tropical-broadleaf-deciduous-forest',
                           'Temperate-or-sub-polar-broadleaf-deciduous-forest',
                           'Mixed-Forest',
                           'Tropical-or-sub-tropical-shrubland',
                           'Temperate-or-sub-polar-shrubland',
                           'Tropical-or-sub-tropical-grassland',
                           'Temperate-or-sub-polar-grassland',
                           'Sub-polar-or-polar-shrubland-lichen-moss',
                           'Sub-polar-or-polar-grassland-lichen-moss',
                           'Sub-polar-or-polar-barren-lichen-moss',
                           'Wetland',
                           'Cropland',
                           'Barren-Lands',
                           'Urban-and-Built-up',
                           'Water',
                           'Snow-and-Ice',]:
            sub.set_xlim(0,1)
            sub.hist(val_attributes[attribute].values,range=(0,1))
        else:
            sub.hist(val_attributes[attribute].values)

        

        if attribute.count('-') > 3:
            attribute_text = '-'.join(attribute.split('-')[0:3])+'-\n'+'-'.join(attribute.split('-')[3:]).replace('broadleaf','brdlf').replace('deciduous','dcds')
        else:
            attribute_text = attribute
        sub.text(0.5,1.03,str2tex(attribute_text,usetex=usetex),
                         verticalalignment='bottom',horizontalalignment='center',
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
    
