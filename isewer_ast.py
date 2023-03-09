import os
import pandas as pd
import numpy as np

from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool, BoxSelectTool
from bokeh.models import ColumnDataSource, RangeTool, MultiChoice, Select, MultiSelect, Spacer,Button, RadioButtonGroup, Band, CDSView, BooleanFilter, BoxAnnotation
from bokeh.palettes import Turbo256#Category20

### TO DO
# - add new voi_label if voi changes
# - venv locally to check speed
# - save current columns when switching month
# - drop NAs of each column on the fly so that lines actually get connected. I.E. different xs for each column
# - rearrange order of year-month 1...12
# - rewrite such that adding columns from left list = add to ColumnDataSource
# -adjust "reset" tool to reset to astart/end of selected month (x_range.update(start=0, end=1) on data update)
# -with resampled data: Check if selection still excludes rows that are in the interval but not shown =  no label even though inside selection...

# Create dict of input file paths
FILES = {}
DATADIR = "/data/isewer/data/012_split_by_year_month/by_month/"
for file in sorted(os.listdir(DATADIR)):
    if ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
        FILES[file[:7]] = DATADIR+file
INITIAL_FILE = "2022_04"
INITIAL_VOI = "Niveau_RÜ_BerlinerAllee"
LABELS = ["Sensor Anomaly", "System Anomaly", "Other"]
LABELCOLORS = ["lightblue", "red","gray"]
new="2022_05"

### WIDGET CALLBACKS
# change month to be plotted

def cb_select_voi(attrname, old, new):
    # add voi Flag columnt to data souce
    nc = select_voi.value + "_Label"
    source.data[nc] = data[nc]
    # redraw plot 0 based on column selection to change visual selection behaviour as voi changes
    cols = multi_list0.value + multi_choice0.value
    draw_ts(ps[0], cols ,source,COLORS, ptype="circle")
    #draw_labels()   

# after selection of anomalous data, select anomaly type
def cb_label_buttons(attrname, old, new):
    #print(new)
    voi_label = select_voi.value + "_Label"
    selected = source.selected.indices
    patch = {voi_label : [(s,new+1) for s in selected]}#NaN =No Label, >0 = one of the labels
    #print(patch)
    source.patch(patch)
    print("patched datasource")
    # redraw labels
    draw_labels()
    print("labels drawn")
    # after operation, reset selected indices + buttons
    source.selected.indices = []
    label_buttons.active = None
    label_buttons.disabled=True

def cb_new_data(attrname, old, new):
    print("updating data..")
    ### Load new data
    data = pd.read_feather(FILES[new])#columns=read_cols
    print("data loaded") 
    data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    cols = INITIALCOLS + multi_list0.value + multi_list1.value + [select_voi.value+"_Label"]
    source.data = data.loc[:,cols]# use from_df?
    print("updated datasource")
    # update xlim of first plot (rest follows)
    ps[0].x_range.update(start=data.DateTime[0], end = data.DateTime[10000])
    print("updated plot limits")
    source.selected.indices = []
    print("cleared selection")
    plot_all(ps, source)

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


### SET UP WIDGETS #1
### Dropdown to choose year
select0 = Select(title="Year/Month", value=INITIAL_FILE, options=list(FILES.keys()))#value=list(FILES.keys())[0]
select0.on_change("value",cb_new_data)

### CREATE DATASOURCE
data = pd.read_feather(FILES[select0.value])#columns=read_cols
print("data loaded") 
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"

# define columns to be available for selection at start
# exclude labes
cols_values = data.columns[~data.columns.str.contains("_Label")]
# choose strang
mask0 = cols_values.str.contains("BerlinerAllee|Uferstraße|Hindenburgstraße|Vogesenstraße")
# define available cols for all plots
#OPTIONS0_0 = sorted(data.columns[mask0 & data.columns.str.contains("Niveau")].to_list()) #includes label columns as well
OPTIONS0 = sorted(cols_values[mask0 & cols_values.str.contains("Niveau")].to_list())
OPTIONS1 = sorted(cols_values[cols_values.str.contains("Niederschlag")].to_list()) + sorted(cols_values[mask0].to_list())
#intial columns are the above including flags of Option0
INITIALCOLS = list(set(["DateTime"] + OPTIONS0 + OPTIONS1 + [c+"_Label" for c in OPTIONS0]))
source = ColumnDataSource(data.loc[:,INITIALCOLS])
print("created datasource")
# save column names
all_cols = cols_values.to_list()
n_all_cols = len(all_cols)

### SET UP WIDGETS #2
### Choice of Variables to plot
#OPTIONS0 = ["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße","Niveau_RÜ_Hindenburgstraße","Niveau_RÜ_Vogesenstraße"]
MULTI_LIST_WIDTH = 220

# Dropdown to set Variable of interest to be labelled
select_voi = Select(title="Variable of Interest", value=INITIAL_VOI, options=OPTIONS0)
select_voi.on_change("value", cb_select_voi)

# Anomaly Label buttons
label_buttons = RadioButtonGroup(labels=LABELS, button_type="warning",disabled=True, width=400)
label_buttons.on_change("active", cb_label_buttons)

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
# Selection for flagging
source.selected.on_change('indices', cb_selection_change)
# Labeling operations
button_safeflags = Button(label="Save flags", button_type="success", height=25)
clearbutton0.on_event('button_click', cb_clearbutton0)

# button2 = Button(label="Delete all flags", button_type="success", height=25)
# button2a = Button(label="Delete selected type of flags", button_type="success", height=25)
# button2b = Button(label="Delete flags in current selection", button_type="success", height=25)
button3 = Button(label="Flag period", button_type="success", height=25)

def cb_clearbutton1(event):
    # data = source.to_df()
    # for label in LABELS:
    #     out[label][:] = (data[label]>0).astype(bool)
    print('saved')


### CREATE PLOTS
TOOLS0 = "pan,box_zoom,wheel_zoom,box_select,reset"#
TOOLS1 = "pan,box_zoom,wheel_zoom,reset"#
WIDTH, HEIGHT = 1500,350
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
pl = figure(width=WIDTH, height=120, x_axis_type="datetime", title='',tools=TOOLS1,x_range=ps[0].x_range, active_drag="pan", active_scroll="wheel_zoom")
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS1, x_range=ps[0].x_range)

# sizing to window (does not work)
#ps[0].sizing_mode = 'scale_width'

# Additional tools (does not work for barchart, so only ps0)
tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
ps[0].add_tools(HoverTool(tooltips=tooltips, mode='mouse', formatters={'@DateTime': 'datetime'}))

# Selection Bar at the bottom
slider = figure(height=100, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#
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
            # if col = voi enable changing appearance of points
            if col == select_voi.value:
                nonselect_alpha = 0.1
                select_color = "orange"
            p.circle(x='DateTime', y=col, size=3,
                            fill_color=COLORS[col], hover_fill_color="firebrick",
                            fill_alpha=0.7, hover_alpha=0.95,
                            line_color=None, hover_line_color="white", legend_label=col, name=col, source=source, nonselection_fill_alpha=nonselect_alpha,
                             selection_color=select_color)
    #top plot: bars
    if ptype == "bar":
        for col in cols:
            p.vbar(x='DateTime', top=col, width=2,
                fill_color=COLORS[col], fill_alpha=1, line_color=COLORS[col], legend_label=col, name=col, source=source, nonselection_fill_alpha=1)# somehow non-selection alpha does not work
# from datetime import datetime as dt
# source.data["DateTime"][0].timestamp()*1000
# pd.Timestamp(source.data["DateTime"][0])*1000

def draw_labels():
#     if pl.legend: 
#         pl.legend.items = []
#     pl.renderers.clear()
#    # for i,label in enumerate(LABELS):
#     #    print(str(i))
#         # filter Label column by levels
    var = select_voi.value+"_Label"
#     # mask = source.data[var] == i+1
#     # view = CDSView(filter=BooleanFilter(mask))
#     # print("created view label "+str(i))
#     i=1
#     label=LABELS[i]
#     pl.circle(x='DateTime', y=var, size=9, source=source, #view=view,
#             alpha=1.0, color=LABELCOLORS[i],line_color=None,
#                 selection_color="orange", legend_label=label)      
#     print("added circles")
#     pl.legend.orientation = "horizontal"
#     pl.legend.location = "top_right"
#     pl.legend.border_line_color = None
    # selected = source.selected.indices
    # if selected:
    #     ind_left = selected[0]
    #     ind_right = selected[-1]
    #     left = (pd.to_datetime(source.data["DateTime"][ind_left]).timestamp())*1000#currentyl no dt support so recalc
    #     right = (pd.to_datetime(source.data["DateTime"][ind_right]).timestamp())*1000
    #     #left, right = source.data["DateTime"][selected[0]], source.data["DateTime"][selected[-1]]
    #     print(left)
    #     print(right)
    #     box = BoxAnnotation(left=left, right=right, fill_alpha=0.2, fill_color="darkorange")
    #     ps[0].add_layout(box)

    # find beginning and end of labeling sequence and draw annotation from start to end
    left, right = np.nan,np.nan
    keepval=np.nan
    for i, val in enumerate(source.data[var]):
        # if a label starts and there was none before
        if (not np.isnan(val)) and (np.isnan(keepval)):
            keepval=val
            ind_left = i
        # if it ends and there was a keepval
        if (np.isnan(val)) and (keepval >= 0):
            keepval=val
            ind_right = i
            left = (pd.to_datetime(source.data["DateTime"][ind_left]).timestamp())*1000#currentyl no dt support so recalc
            right = (pd.to_datetime(source.data["DateTime"][ind_right]).timestamp())*1000
            box = BoxAnnotation(left=left, right=right, fill_alpha=0.2, fill_color="darkorange")
            ps[0].add_layout(box)
        # Not implemented: if first category 1, then category 2

def plot_all(ps, source):
    cols = [multi_choice0.value,multi_choice1.value]
    PTYPES = ["circle","bar"]
    for p_i in range(len(ps)):
        draw_ts(ps[p_i], cols[p_i],source,COLORS, ptype=PTYPES[p_i])
        ps[p_i].legend.location = "top_left"
        ps[p_i].legend.click_policy="hide"
    draw_labels()

# initial set-up
plot_all(ps, source)

s  = slice(pd.to_datetime("2022-04-01 13:13:00"),pd.to_datetime("2022-04-01 13:15:00"))
data1 = data.set_index("DateTime")
data1["2022-04-01 13:13:00":"2022-04-01 13:15:00"]

### FILTERINGd
#view = CDSView(filter=IndexFilter([0, 2, 4]))
#p2.circle(x="x", y="y", size=10, hover_color="red", source=source, view=view)

# for obj in [ps[0], ps[1], select0, multi_list0,multi_choice0, select,multi_choice1]:
#     obj.sizing_mode = 'scale_both'
#layout.sizing_mode = 'scale_both'


# col0 = column(select0, multi_list0, multi_list1)
# col1 = column(multi_choice0, ps[0],multi_choice1, ps[1],slider)
# layout = row(col0, col1)


row0 = row(select0, select_voi, label_buttons)
row1 = row(column(multi_list0, clearbutton0),column(multi_choice0, ps[0],pl))
row2 = row(column(multi_list1, clearbutton1),column(multi_choice1, ps[1]))
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0,row1,row2,row3)
curdoc().add_root(layout)
curdoc().title = "i-SEWER Anomaly Selection Tool"


### IDEAS to UPDATE DATA SOURCE WHEN CHOOSING OTHER MONTH

## TWO WAYS To ACHIEVE DROP DOWN THAT CHANGES COLUMNS SHOWN
# - clean renderers entirely and re-plot in callback
# - Preferred: create renderer list for all columns, fill/empty those that change
# - create all plots, toggle visibility in callback

#--> see CML
# def update(selected=None):
#     cml_id = ticker2.value
#     month = ticker1.value
#     data, meta = get_data(cml_id, month)
#     source.data = data
#     source_static.data = data


### Am nächsten dran:
#   https://stackoverflow.com/questions/38038432/bokeh-interactively-changing-the-columns-being-plotted
#https://stackoverflow.com/questions/61145046/dynamically-adding-and-removing-bokeh-legends
### Am vielversprechendsten: Alle plotts, aber nicht alle visible
#https://stackoverflow.com/questions/69462392/hide-several-lines-using-checkboxes-and-customjs-in-python-bokeh
#inkl Legende
#https://discourse.bokeh.org/t/confusion-on-customjs-for-filtering-with-multichoice/8830

# Generally: Advised to create all glyphs upfront, then toggle visibility (https://stackoverflow.com/questions/56787879/how-can-i-speed-up-update-of-select-multiselect-widgets-in-bokeh)   

# f you just have one simple plot with a legend then you can probably:

# remove the associated GlyphRenderer from p.renderers
# delete the corresponding LegendItem from the Legend

### CHANGE COLOR USING JSCallback
#https://stackoverflow.com/questions/48451710/bokeh-can-only-update-column-via-callback-once


### Change Glyph field JSCallback
#https://stackoverflow.com/questions/56518957/bokeh-python-how-to-change-data-columns-in-customjs-callback
#r = p.line(x='x', y='foo' source=source)
# cb = CustomJS(args=dict(r=r, select=select), code="""
#     // tell the glyph which field of the source y should refer to
#     r.glyph.y.field = select.value

#     // manually trigger change event to re-render
#     r.glyph.change.emit()
# """)


#You need to pass a ColumnDataSource with the data as a second argument to to p.add_glyph. The field specifications are references to columns in a CDS. All that said, a much better approach in general would be add all the glyphs up front and use the select callback to toggle their visibility as appropriate.


# import matplotlib.pyplot as plt
# ax = data.set_index("DateTime").loc[:,cols].plot(marker="o", linestyle='none', ms=1)
# ax.figure.savefig("test.png")
