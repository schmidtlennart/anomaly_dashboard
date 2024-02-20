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
from isewer_ast.plotting import wdraw_ts, wdraw_labels, create_colors
from isewer_ast.dashboard_elements import create_plot_objects
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
source = ColumnDataSource(alldata.loc[:,columns_to_pr_label([INITIAL_COLS0, INITIAL_COLS1])])
print("created datasource")



COLORS = create_colors(data.columns.to_list() + data_pr.columns.to_list())
# central variables to hold variables currently in plots 0 and 1
# accessed inside functions also
current_cols0 = INITIAL_COLS0
current_cols1 = INITIAL_COLS1
#current_labels = [c+"_Label" for c in current_cols0 if not c=="pr_DateTime"]
current_voi = INITIAL_VOI

################## PLOTS #############################
ps, pl, slider = create_plot_objects(data, current_voi)

################## WIDGETS & BUTTONS #############################
select_ym, select_voi, multi_list0, multi_list1, multi_choice0, multi_choice1 = create_widgets(all_cols, OPTIONS0, OPTIONS1)
clearbutton0, clearbutton1, label_buttons, button_delete_sel_labels, button_delete_all_labels, button_save_all_labels = create_buttons()

# Set up plotting functions
plot_args = {"ps": ps, "pl": pl, "source": source, "select_voi": select_voi, "multi_choice0": multi_choice0, "multi_list0": multi_list0, "multi_choice1": multi_choice1, "multi_list1": multi_list1}
#plot_all(ps, pl, source, select_voi, multi_choice0, multi_list0, multi_choice1, multi_list1)
# create plotting functions from closure so I dont have to pass all objects to all callbacks
draw_labels = wdraw_labels(**plot_args)
draw_ts = wdraw_ts(**plot_args)

#### CALLBACKS
# set callbacks (need above plotting functions from global scope)
# Dropdown to set Variable of interest to be labelled
voi_args = {"source": source, "all_cols0":all_cols, "ps": ps, "pl": pl, "COLORS": COLORS}
args = {"multi_list0": multi_list0,"multi_list1": multi_list1, "source": source, "COLORS": COLORS, "ps": ps, "pl":pl, "select_voi":select_voi}
# Labelling actions only allowed if data is selected
source.selected.on_change('indices', cb_selection_change)

select_ym.on_change("value",cb_new_data)
select_voi.on_change("value", wcb_select_voi(**voi_args))
multi_list0.on_change("value", cb_multi_list0)
multi_list1.on_change("value", cb_multi_list1)

# Button Callbacks
#clearbutton0.on_event('button_click', cb_clearbutton0)
#clearbutton1.on_event('button_click', cb_clearbutton1)
#label_buttons.on_change("active", cb_set_labels)
button_delete_sel_labels.on_event('button_click', cb_delete_sel_labels)
button_delete_all_labels.on_event('button_click', cb_delete_all_labels)
button_save_all_labels.on_event('button_click', cb_save_all_labels)

### START SERVER
plot_all(**plot_args)

### DASHBOARD LAYOUT
row0 = row(select_ym,select_voi)
#row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0),column(multi_choice0, ps[0],pl))# button_delete_all_labels, button_save_all_labels
row2 = row(column(multi_list1, clearbutton1),column(multi_choice1, ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row1,row2,row3)#row01
curdoc().add_root(layout)
curdoc().title = "i-SEWER Classifications"# apply theme to current document
