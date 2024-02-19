### FIXING DATA SAVING BUG
# .copy()
# bokeh source.update_DataSource o.ä.
# print source.data vs. outdata vs data

##TODO:
# - revert temporary datetime fix in initial data loading & cb_new_data
# fix zooming: resetting, separate x&y zooming/manual

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
from isewer_ast.helpers import get_filenames
from isewer_ast.plotting import draw_ts, draw_labels, plot_all, create_colors

# read montly input file names
FILES, FILES_PR = [get_filenames(f) for f in [DATADIR, DATADIR_CL]]

### SET UP WIDGETS #1
### Dropdown to choose year
select_ym = Select(title="Year/Month", value=INITIAL_FILE, options=list(FILES.keys()))#value=list(FILES.keys())[0]
select_ym.on_change("value",cb_new_data)

### CREATE DATASOURCE
# observed
data = pd.read_feather(FILES[select_ym.value])#columns=read_cols
print("data loaded") 
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
# predictions
data_pr = pd.read_feather(FILES_PR[select_ym.value])#columns=read_cols
print("data_pr loaded") 

####################TEMPORARY FIX
#data_pr["DateTime"] = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
####################!!

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
# define columns to be available for selection/loaded at start
cols_values = data.columns
# choose strang
mask0 = cols_values.str.contains("BerlinerAllee|Uferstraße|Hindenburgstraße|Vogesenstraße")
# define available cols for all plots
# all Niveaus
OPTIONS0 = sorted(cols_values[mask0 & cols_values.str.contains("Niveau")].to_list())
OPTIONS1 = ["FSR_Rückwärts_RÜ_Hindenburgstraße"]+sorted(cols_values[cols_values.str.contains("Niederschlag")].to_list()) + sorted(cols_values[mask0].to_list())
#intial columns are the above including labels of Option0
INITIALCOLS = list(set(["DateTime"] + OPTIONS0 + OPTIONS1))
INITIALCOLS_PR = ["pr_"+c for c in INITIALCOLS] + ["pr_" + c+"_Label" for c in INITIALCOLS]
# drop if "pr_DateTime_Label"
INITIALCOLS_PR = [c for c in INITIALCOLS_PR if not c=="pr_DateTime_Label"]
print(INITIALCOLS_PR)
### merge predictions and observed data
alldata = pd.concat([data,data_pr_plot], axis=1)

source = ColumnDataSource(alldata.loc[:,INITIALCOLS+INITIALCOLS_PR])
print("created datasource")
# save column names
all_cols = data.columns.to_list() + data_pr.columns.to_list()
COLORS = create_colors(all_cols)

### SET UP WIDGETS #2

# Dropdown to set Variable of interest to be labelled
select_voi = Select(title="Variable of Interest", value=INITIAL_VOI, options=sorted(all_cols))#, options=OPTIONS0)
select_voi.on_change("value", cb_select_voi)


### CREATE PLOTS
TOOLS0 = "pan,box_zoom,ywheel_zoom,box_select,reset"#
TOOLS1 = "pan,box_zoom,ywheel_zoom,reset"#
WIDTH, HEIGHT = 1500,350
HEIGHT1 = 100


# Basic plot setup
ps = [[],[]]#holds timeseries
xleft = data.DateTime[0]
xright = data.DateTime[10000]
ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS0,x_range=(xleft,xright), active_drag="pan", active_scroll="ywheel_zoom")#, output_backend="webgl"#webgl=GPU acceleration, causes problems with vbar
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS1, x_range=ps[0].x_range)
# holds labels
pl = figure(width=WIDTH, height=HEIGHT1, x_axis_type="datetime", title='',tools="box_select",toolbar_location=None, y_axis_type=None,x_range=ps[0].x_range, y_range=(0,1), active_drag="box_select")
pl.ygrid.grid_line_color = None

# sizing to window (does not work)
#ps[0].sizing_mode = 'scale_width'

# Additional tools (does not work for barchart, so only ps0)
tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
hover = HoverTool(tooltips=tooltips, mode='mouse', formatters={'@DateTime': 'datetime'})
ps[0].add_tools(hover)

# Selection Bar at the bottom
slider = figure(height=HEIGHT1, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#
range_tool = RangeTool(x_range=ps[0].x_range)#
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

slider.circle(x='DateTime', size=3,y=select_voi.value,fill_color="darkgray",line_color=None, fill_alpha=0.7, source=source)#olors[0]
slider.ygrid.grid_line_color = None
slider.add_tools(range_tool)
#slider.toolbar.active_multi = range_tool


### SET UP WIDGETS #3

# Additional variables plot 1
multi_list0 =  MultiSelect(options=sorted(all_cols), title="Strg+Click to deselect", size=23, width=MULTI_LIST_WIDTH)
multi_list0.on_change("value", cb_multi_list0)
# Additional variables plot 2
multi_list1 =  MultiSelect(options=sorted(all_cols), size=23, width=MULTI_LIST_WIDTH)
multi_list1.on_change("value", cb_multi_list1)
# Berliner Strang variables
multi_choice0 = MultiChoice(value=["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"], options=OPTIONS0)
# need to pass objcets to callback, so we wrap inside lambda
args = {"multi_list0": multi_list0,"multi_list1": multi_list1, "source": source, "COLORS": COLORS, "ps": ps, "select_voi":select_voi}

#lambda attr, old, new: cb_new_cols0(attr, old, new, **args)

multi_choice0.on_change("value", wcb_new_cols0(**args))# NSM Variables

multi_choice1 = MultiChoice(value=["FSR_Rückwärts_RÜ_Hindenburgstraße"], options=OPTIONS1)#"Niederschlag_Schwarzer_Steg"
multi_choice1.on_change("value", wcb_new_cols1(**args))

# Emptying multilist0
clearbutton0 = Button(label="clear")
clearbutton0.on_event('button_click', cb_clearbutton0)
# Emptying multilist1
clearbutton1 = Button(label="clear")
clearbutton1.on_event('button_click', cb_clearbutton1)
# Labelling actions only allowed if data is selected
source.selected.on_change('indices', cb_selection_change)

### LABELLING
# Anomaly Label buttons, Set label if pressed
label_buttons = RadioButtonGroup(labels=LABELS, button_type="primary",disabled=True, width=1500, height=35)
label_buttons.on_change("active", cb_set_labels)
# delete labels in current selection
button_delete_sel_labels = Button(label="Delete labels in selection", button_type="danger", height=35, width=500,disabled=True)
button_delete_sel_labels.on_event('button_click', cb_delete_sel_labels)
#delete all labels that were set
button_delete_all_labels = Button(label="Delete all labels", button_type="danger", height=25)
button_delete_all_labels.on_event('button_click', cb_delete_all_labels)
# save all labels to feather-file
button_save_all_labels = Button(label="Save labels to file", button_type="success", height=25)
button_save_all_labels.on_event('button_click', cb_save_all_labels)





####### START SERVER
# initial set-up
plot_all(ps, pl, source, select_voi, multi_choice0, multi_list0, multi_choice1, multi_list1)

row0 = row(select_ym,select_voi)
#row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0),column(multi_choice0, ps[0],pl))# button_delete_all_labels, button_save_all_labels
row2 = row(column(multi_list1, clearbutton1),column(multi_choice1, ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row1,row2,row3)#row01
curdoc().add_root(layout)
curdoc().title = "i-SEWER Classifications"# apply theme to current document

# import time
# # for testing of datasource problem
# for m in ["2021_03","2022_02","2021_05"]:
#     print(m)
#     select_ym.value = m
#     time.sleep(10)
### IDEAS to UPDATE DATA SOURCE WHEN CHOOSING OTHER MONTH
## TWO WAYS To ACHIEVE DROP DOWN THAT CHANGES COLUMNS SHOWN
# - clean renderers entirely and re-plot in callback
# - Preferred: create renderer list for all columns, fill/empty those that change
# - create all plots, toggle visibility in callback
