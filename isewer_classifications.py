### FIXING DATA SAVING BUG
# .copy()
# bokeh source.update_DataSource o.ä.
# print source.data vs. outdata vs data

##TODO:
# fix zooming: resetting, separate x&y zooming/manual
# fix resetting after YM change
# OPTIONAL:
# update slider inside drawing functions as well

import os
import pandas as pd
import numpy as np
import random
from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool, BoxSelectTool
from bokeh.models import ColumnDataSource, RangeTool, MultiChoice, Select, MultiSelect, Spacer,Button, Range1d, RadioButtonGroup, Band, CDSView, BooleanFilter, BoxAnnotation, Legend, LegendItem
from bokeh.palettes import Turbo256#Category20

from isewer_ast.callbacks import *
from isewer_ast.constants import *
from isewer_ast.helpers import get_filenames, create_data_source
from isewer_ast.plotting import create_colors, plot_all
from isewer_ast.dashboard_elements import create_plot_objects, create_widgets, create_buttons
# read montly input file names
FILES, FILES_PR = [get_filenames(f) for f in [DATADIR, DATADIR_CL]]

### CREATE DATASOURCE & GET RELEVANT COLUMNS
source, alldata, allcols = create_data_source(FILES, FILES_PR, INITIAL_FILE, [INITIAL_COLS0, INITIAL_COLS1])

COLORS = create_colors(alldata.columns.to_list())

################## WIDGETS & BUTTONS #############################
select_ym, select_voi, multi_list0, multi_list1 = create_widgets(FILES, allcols)
clearbutton0, clearbutton1, label_buttons, button_delete_sel_labels, button_delete_all_labels, button_save_all_labels = create_buttons()

################## PLOTS #############################
ps, pl, slider = create_plot_objects(alldata, select_voi, source)

# Set up plotting functions

#### CALLBACKS
# set callbacks (need above plotting functions from global scope)
# Labelling actions only allowed if data is selected
source.selected.on_change('indices', wcb_selection_change(label_buttons, button_delete_sel_labels))

# All objects needed in callbacks
# TO DO: Turn into class object that I can simply pass around (=only one kw argument)
args = {"FILES":FILES, "FILES_PR":FILES_PR, "source": source, "alldata":alldata, "allcols":allcols, "COLORS": COLORS, "ps": ps, "pl":pl, "slider":slider,"select_voi":select_voi, "multi_list0":multi_list0, "multi_list1":multi_list1}
select_ym.on_change("value",wcb_new_data(**args))#change of month
select_voi.on_change("value", wcb_select_voi(**args))#change of Variable of Interest
multi_list0.on_change("value", wcb_multi_list0(**args))# change of selection in multilist0
multi_list1.on_change("value", wcb_multi_list1(**args))# change of selection in multilist1

# Button Callbacks
### THESE DO NOT WORK IF IMPORTED FROM CALLBACKS.PY


clearbutton0.on_event('button_click', wcb_clearbutton0(multi_list0=multi_list0))
clearbutton1.on_event('button_click', wcb_clearbutton1(multi_list1=multi_list1))

#label_buttons.on_change("active", cb_set_labels)
# button_delete_sel_labels.on_event('button_click', cb_delete_sel_labels)
# button_delete_all_labels.on_event('button_click', cb_delete_all_labels)
# button_save_all_labels.on_event('button_click', cb_save_all_labels)

### START SERVER
plot_all(**args)

### DASHBOARD LAYOUT
row0 = row(select_ym,select_voi)
#row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0),column(ps[0],pl))# button_delete_all_labels, button_save_all_labels
row2 = row(column(multi_list1, clearbutton1),column(ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row1,row2,row3)#row01
curdoc().add_root(layout)
curdoc().title = "i-SEWER Classifications"# apply theme to current document
