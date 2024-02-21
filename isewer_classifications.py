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
from isewer_ast.helpers import get_filenames, columns_to_pr_label
from isewer_ast.plotting import create_colors, plot_all
from isewer_ast.dashboard_elements import create_plot_objects, create_widgets, create_buttons
# read montly input file names
FILES, FILES_PR = [get_filenames(f) for f in [DATADIR, DATADIR_CL]]

### CREATE DATASOURCE & GET RELEVANT COLUMNS
# observed
data = pd.read_feather(FILES[INITIAL_FILE])#columns=read_cols
print("data loaded") 
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
# predictions
data_pr = pd.read_feather(FILES_PR[INITIAL_FILE])#columns=read_cols
print("data_pr loaded") 

# reduce both to the inner join set of columns, i.e. also remove labels
cols_joint_label = list(set(data.columns.to_list())& set(data_pr.columns.to_list()))
# drop all with _Label
cols_joint = [c for c in cols_joint_label if not c.endswith("_Label")]
data = data.loc[:,cols_joint]
# add labels back in
data_pr = data_pr.loc[:,cols_joint+cols_joint_label]
# rename to make clear that its predicions
data_pr.columns = ["pr_"+c for c in data_pr.columns]
# recode labels 0 to np.nan forplotting
data_pr_plot = data_pr.copy()
data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")] = data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")].replace({0:np.nan})

### merge predictions and observed data
alldata = pd.concat([data,data_pr_plot], axis=1)
initial_load_cols = ["DateTime"] + columns_to_pr_label([INITIAL_COLS0, INITIAL_COLS1])
source = ColumnDataSource(alldata.loc[:,initial_load_cols])
print("created datasource")

COLORS = create_colors(alldata.columns.to_list())

# dynamic variables to hold variables currently in plots 0 and 1
# accessed inside functions also
current_cols0 = INITIAL_COLS0
current_cols1 = INITIAL_COLS1
#current_labels = [c+"_Label" for c in current_cols0 if not c=="pr_DateTime"]
current_voi = INITIAL_VOI

################## PLOTS #############################
ps, pl, slider = create_plot_objects(data, current_voi, source)

################## WIDGETS & BUTTONS #############################
select_ym, select_voi, multi_list0, multi_list1 = create_widgets(FILES, data.columns, INITIAL_COLS0, INITIAL_COLS1)
clearbutton0, clearbutton1, label_buttons, button_delete_sel_labels, button_delete_all_labels, button_save_all_labels = create_buttons()

# Set up plotting functions
plot_args = {"ps": ps, "pl": pl, "source": source, "current_voi": current_voi, "current_cols0":current_cols0, "current_cols1":current_cols1, "COLORS":COLORS}

#### CALLBACKS
# set callbacks (need above plotting functions from global scope)
# Dropdown to set Variable of interest to be labelled

# Labelling actions only allowed if data is selected
source.selected.on_change('indices', wcb_selection_change(label_buttons, button_delete_sel_labels))

args = {"source": source, "alldata":alldata, "COLORS": COLORS, "ps": ps, "pl":pl, "current_voi":current_voi, "current_cols0":current_cols0, "current_cols1":current_cols1, "multi_list0":multi_list0}
ctx = {}
#select_ym.on_change("value",cb_new_data)#change of month
select_voi.on_change("value", wcb_select_voi(**args))#change of Variable of Interest
multi_list0.on_change("value", wcb_multi_list0(**args))# change of selection in multilist0
multi_list1.on_change("value", wcb_multi_list1(**args))# change of selection in multilist1

# Button Callbacks
### THESE DO NOT WORK IF IMPORTED FROM CALLBACKS.PY
def cb_clearbutton0():
    # empty multilist and replot only multicolumn selections
    multi_list0.value = []
    #draw_ts(ps[0], multi_choice0.value ,source,COLORS, ptype="circle")

def cb_clearbutton1():
    # empty multilist and replot only multicolumn selections
    multi_list1.value = []
    #draw_ts(ps[1], multi_choice1.value ,source,COLORS, ptype="bar")


clearbutton0.on_event('button_click', cb_clearbutton0)
clearbutton1.on_event('button_click', cb_clearbutton1)
#label_buttons.on_change("active", cb_set_labels)
# button_delete_sel_labels.on_event('button_click', cb_delete_sel_labels)
# button_delete_all_labels.on_event('button_click', cb_delete_all_labels)
# button_save_all_labels.on_event('button_click', cb_save_all_labels)

### START SERVER
plot_all(**plot_args)

### DASHBOARD LAYOUT
row0 = row(select_ym,select_voi)
#row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0),column(ps[0],pl))# button_delete_all_labels, button_save_all_labels
row2 = row(column(multi_list1, clearbutton1),column(ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row1,row2,row3)#row01
curdoc().add_root(layout)
curdoc().title = "i-SEWER Classifications"# apply theme to current document
