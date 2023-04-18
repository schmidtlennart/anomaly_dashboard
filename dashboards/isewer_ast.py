import os
import pandas as pd
import numpy as np

from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool, BoxSelectTool
from bokeh.models import ColumnDataSource, RangeTool, MultiChoice, Select, MultiSelect, Spacer,Button, RadioButtonGroup, Band, CDSView, BooleanFilter, BoxAnnotation, Legend, LegendItem
from bokeh.palettes import Turbo256#Category20
from bokeh.transform import linear_cmap

### TO DO

# Christian
# - dritter Plot für Enlastungsereigenisse ja/nein etc.
# - Reduce Alpha of plots so that all can be seen
#- muting during selection only the selected one

#PRIO 1
# - Abfack wenn Neuer Monat geladen aber alter drin - überschreibt beim Wechsel die Daten. 1) nur flags speichern (mache ich ?) oder 2) nur speichern direkt wenn wenn falgs gesetzt werden
# - Move rangetool by left+right arrow keys
# - rearrange order of year-month 1...12
# - arrange multilists by bauwerk
# - enable selection of Strang to be labelled at startup
# - adjust "reset" tool to reset to astart/end of selected month (x_range.update(start=0, end=1) on data update)
# -set persistent seed
# wheel zoom: Only in x-axis (zooming in sometimes doesnt go back)

#PRIO 2
# add bar vs circle to plot 2 or add 3rd plot entirely free
# - with resampled data: Check if selection still excludes rows that are in the interval but not shown =  no label even though inside selection.
# - with resampeld data: vline instead of circle
# - venv locally to check speed
# - "restart me"-button


# Create dict of input file paths
FILES = {}
DATADIR = "/data/isewer/data/011_split_by_year_month/by_month/"
for file in sorted(os.listdir(DATADIR)):
    if ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
        FILES[file[:7]] = DATADIR+file
INITIAL_FILE = "2021_12"
INITIAL_VOI = "Niveau_RÜ_BerlinerAllee"
LABELS = ["Sensor Anomaly", "System Anomaly", "Other"]
LABELCOLORS = ["lightblue", "darkred","gray"]

### WIDGET CALLBACKS
# change month to be plotted

def cb_select_voi(attrname, old, new):
    # redraw plot 0 based on column selection to change visual selection behaviour as voi changes
    #cols = list(set(multi_list0.value + multi_choice0.value + [new]))
    cols=multi_list0.value + multi_choice0.value
    draw_ts(ps[0], cols ,source,COLORS, ptype="circle")
    #redraw labels
    draw_labels()

def cb_new_data(attrname, old, new):
    print("updating data..")
    ### save current data to file
    print(f"old: {old}")
    print(f"new: {new}")
    #cb_save_all_labels(old)
    ### Load new data
    data = pd.read_feather(FILES[new])#columns=read_cols
    print("data loaded") 
    data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    cols0 = INITIALCOLS + multi_list0.value + multi_list1.value
    source.data = data.loc[:,cols0]#.to_dict()# use from_df?
    print("updated datasource")
    # update xlim of first plot (rest follows)
    ps[0].x_range.update(start=data.DateTime[0], end = data.DateTime[10000])
    #print("updated plot limits")
    source.selected.indices = []
    #print("cleared selection")
    plot_all(ps, source)
    print("new head indices")
    print(source.data["DateTime"][:1])
    print("Data indices")
    print(data.DateTime[:1])
   
def cb_new_cols0 (attrname, old, new):
    # redraw plot 0 based on column selection
    cols = new + multi_list0.value
    draw_ts(ps[0], cols ,source,COLORS, ptype="circle")

def cb_new_cols1 (attrname, old, new):
    # redraw plot 2 based on columns selection
    cols = new + multi_list1.value
    draw_ts(ps[1], cols ,source,COLORS, ptype="bar")

def cb_multi_list0 (attrname, old, new):
    # add respective columns to datasource
    newcols = list(set(new)-set(source.data.keys()))
    print("adding cols: \n")
    print(newcols)
    for nc in newcols:
        source.data[nc] = data[nc]
    # add all cols from this list to multichoice0.value & plot 0 redraw
    cols = multi_choice0.value + new
    draw_ts(ps[0], cols ,source,COLORS, ptype="circle")  

def cb_multi_list1 (attrname, old, new):
    # add respective columns to datasource (if not existant yet)
    newcols = list(set(new)-set(source.data.keys()))
    print("adding cols: \n")
    print(newcols)
    for nc in newcols:
        source.data[nc] = data[nc]
    # add all cols from this list to multichoice1.value & plot 1 redraw
    cols = multi_choice1.value + new
    draw_ts(ps[1], cols ,source,COLORS, ptype="bar")  

def cb_clearbutton0():
    # empty multilist and replot only multicolumn selections
    multi_list0.value = []
    draw_ts(ps[0], multi_choice0.value ,source,COLORS, ptype="circle")

def cb_clearbutton1():
    # empty multilist and replot only multicolumn selections
    multi_list1.value = []
    draw_ts(ps[1], multi_choice1.value ,source,COLORS, ptype="bar")

def cb_selection_change (attrname, old, new):
        label_buttons.disabled=False
        button_delete_sel_labels.disabled=False


### LABELLING
# after selection of anomalous data, save flag into data
def cb_set_labels(attrname, old, new):
    #print(new)
    voi_label = select_voi.value + "_Label"
    selected = source.selected.indices
    if selected:
        patch = {voi_label : [(s,(new+1)/10) for s in selected]}#NaN =No Label, >0 = one of the labels
        #print(patch)
        source.patch(patch)
        print("patched datasource")
    # after operation, reset selected indices + buttons
    source.selected.indices = []
    label_buttons.active = None
    label_buttons.disabled=True
    button_delete_sel_labels.disabled=True
# delte labels in selection
def cb_delete_sel_labels():
    voi_label = select_voi.value + "_Label"
    selected = source.selected.indices
    if selected:
        #NaN =No Label, >0 = one of the labels, either 0.1,0.2 or 0.3. +1 for values starting with 1 / 10 = 0.1
        patch = {voi_label : [(s,np.nan) for s in selected]}
        source.patch(patch)
    # after operation, reset selected indices + buttons
    source.selected.indices = []
    label_buttons.active = None
    label_buttons.disabled=True
    button_delete_sel_labels.disabled=True
# delete all labels of current month
def cb_delete_all_labels():
    voi_label = select_voi.value + "_Label"
    source.data[voi_label] = np.repeat(np.nan, len(source.data[voi_label]))
# save all labels of current month to feather-file
def cb_save_all_labels(old=None):
    # old: if called via cb_select_ym, save old data using old ym
    outdata = source.to_df()
    outdata = outdata.loc[:,outdata.columns.str.contains("_Label")]
    data.loc[:,outdata.columns] = outdata
    ym = old if old else select_ym.value
    print(f"Old from selection: {old}")
    print(f"Saving to: {ym}")
    print("Data indices")
    print(data.DateTime[:1])### HIER HAT ER IMMER NOCH APRIL, aber irgwie nur in dieser Funktion
    data.to_feather(FILES[ym])
    print("saved data")

### SET UP WIDGETS #1
### Dropdown to choose year
select_ym = Select(title="Year/Month", value=INITIAL_FILE, options=list(FILES.keys()))#value=list(FILES.keys())[0]
select_ym.on_change("value",cb_new_data)

### CREATE DATASOURCE
data = pd.read_feather(FILES[select_ym.value])#columns=read_cols
print("data loaded") 
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"

# define columns to be available for selection at start
# exclude labels
cols_values = data.columns[~data.columns.str.contains("_Label")]
# choose strang
mask0 = cols_values.str.contains("BerlinerAllee|Uferstraße|Hindenburgstraße|Vogesenstraße")
# define available cols for all plots
# all Niveaus
OPTIONS0 = sorted(cols_values[mask0 & cols_values.str.contains("Niveau")].to_list())
OPTIONS1 = sorted(cols_values[cols_values.str.contains("Niederschlag")].to_list()) + sorted(cols_values[mask0].to_list())
#OPTIONS0 = list(reversed(OPTIONS1))
#intial columns are the above including labels of Option0
INITIALCOLS = list(set(["DateTime"] + OPTIONS0 + OPTIONS1 + [c+"_Label" for c in OPTIONS1]))
source = ColumnDataSource(data.loc[:,INITIALCOLS])
print("created datasource")
# save column names
all_cols = cols_values.to_list()
n_all_cols = len(all_cols)

### SET UP WIDGETS #2
### Choice of Variables to plot
MULTI_LIST_WIDTH = 220

# Dropdown to set Variable of interest to be labelled
select_voi = Select(title="Variable of Interest", value=INITIAL_VOI, options=list(reversed(OPTIONS1)))
select_voi.on_change("value", cb_select_voi)

# Berliner Strang variables
multi_choice0 = MultiChoice(value=["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"], options=OPTIONS0)
multi_choice0.on_change("value", cb_new_cols0)
# NSM Variables
multi_choice1 = MultiChoice(value=["Niederschlag_Schwarzer_Steg", 'Niederschlag_Clara_Immerwahr_Straße', 'Niederschlag_Günterstal'], options=OPTIONS1)
multi_choice1.on_change("value", cb_new_cols1)
# Additional variables plot 1
multi_list0 =  MultiSelect(options=sorted(all_cols), title="Strg+Click to deselect", size=23, width=MULTI_LIST_WIDTH)
multi_list0.on_change("value", cb_multi_list0)
# Additional variables plot 2
multi_list1 =  MultiSelect(options=sorted(all_cols), size=23, width=MULTI_LIST_WIDTH)
multi_list1.on_change("value", cb_multi_list1)
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


### CREATE PLOTS
TOOLS0 = "pan,box_zoom,wheel_zoom,box_select,reset"#
TOOLS1 = "pan,box_zoom,wheel_zoom,reset"#
WIDTH, HEIGHT = 1500,350
HEIGHT1 = 100
# get one color for each variable
np.random.seed(12)#to keep colors the same
rand_seq = np.random.choice(n_all_cols,n_all_cols, replace=False)#randomize colors to get distiniguihsable colors from conitnous colormap
color_seq = [Turbo256[r] for r in rand_seq]
COLORS = dict(zip(all_cols,color_seq))

# Basic plot setup
ps = [[],[]]#holds timeseries
xleft = data.DateTime[0]
xright = data.DateTime[10000]
ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS0,x_range=(xleft,xright), active_drag="pan", active_scroll="wheel_zoom")#, output_backend="webgl"#webgl=GPU acceleration, causes problems with vbar
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS0, x_range=ps[0].x_range)
# holds labels
pl = figure(width=WIDTH, height=HEIGHT1, x_axis_type="datetime", title='',tools="box_select",toolbar_location=None, y_axis_type=None,x_range=ps[0].x_range, y_range=(0,0.4), active_drag="box_select")
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
slider.toolbar.active_multi = range_tool


### PLOTTING FUNCTIONS
def draw_ts(p, cols, source, COLORS, ptype):
    # Plots either one of the timeseries plots
    # ptype: "circle" or "bar", plotting type
    if p.legend: 
        p.legend.items = []
    p.renderers.clear()
    # top plot: circles
    if ptype == "circle":
        for col in cols:
            nonselect_alpha = 0.9
            select_color = COLORS[col]
            size=2
            # if col = voi enable changing appearance of points
            if col == select_voi.value:
                nonselect_alpha = 0.1
                select_color = "orange"
                size = 3.5
            p.circle(x='DateTime', y=col, size=size,
                            fill_color=COLORS[col], hover_fill_color="firebrick",
                            fill_alpha=0.7, hover_alpha=0.95,
                            line_color=None, hover_line_color="white", legend_label=col, name=col, source=source, nonselection_fill_alpha=nonselect_alpha,
                             selection_color=select_color)
    #bottom plot: bars
    if ptype == "bar":
        for col in cols:
            ns_fill_alpha=0.9
            select_color = COLORS[col]
            width = 2           
            if col == select_voi.value:
                ns_fill_alpha=0.2
                select_color = "orange"
                width = 3.5
            p.vbar(x='DateTime', top=col, width=width,
                fill_color=COLORS[col], fill_alpha=1, line_color=COLORS[col], selection_fill_color=select_color, legend_label=col, name=col, source=source, nonselection_fill_alpha=ns_fill_alpha)# somehow non-selection alpha does not work
# from datetime import datetime as dt
# source.data["DateTime"][0].timestamp()*1000
# pd.Timestamp(source.data["DateTime"][0])*1000

def draw_labels():
    if pl.legend: 
        pl.legend.items = []
    pl.renderers.clear()
    var = select_voi.value+"_Label"
    cmap = linear_cmap(field_name=var, palette=LABELCOLORS, low=(0.1), high=0.3)
    pl.rect(x='DateTime', y=var, width=80000, height=1, source=source,#size=16
           fill_alpha=1, fill_color=cmap,line_color=None,#,#"color"
                selection_color="orange")
    print("added label circles")
    # Hacky custom label legend these are a dummy glyphs to help draw the legend
    dummy_rs = [pl.circle(x=[0, 0], y=[0, 0], line_width=1, color=c,line_color=None, name='dummy_for_legend') for c in LABELCOLORS]
    legend = Legend(items=[LegendItem(label=l, renderers=[r]) for l,r in zip(LABELS,dummy_rs)],
        location="top_right", orientation="horizontal",
        border_line_color=None)
    pl.add_layout(legend)

def plot_all(ps, source):
    cols = [multi_choice0.value+multi_list0.value, multi_choice1.value+multi_list1.value]
    PTYPES = ["circle","bar"]
    for p_i in range(len(ps)):
        draw_ts(ps[p_i], cols[p_i],source,COLORS, ptype=PTYPES[p_i])
        ps[p_i].legend.location = "top_left"
        ps[p_i].legend.click_policy="hide"
    draw_labels()
    # pl.legend.orientation = "horizontal"
    # pl.legend.location = "top_right"
    # pl.legend.border_line_color = None


# initial set-up
plot_all(ps, source)

row0 = row(select_ym, select_voi)
row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0, button_delete_all_labels, button_save_all_labels),column(multi_choice0, ps[0],pl))
row2 = row(column(multi_list1, clearbutton1),column(multi_choice1, ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row01,row1,row2,row3)
curdoc().add_root(layout)
curdoc().title = "i-SEWER Anomaly Selection Tool"# apply theme to current document

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
