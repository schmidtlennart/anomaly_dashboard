import os
import pandas as pd
import numpy as np

from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, RangeTool, CustomJS, MultiChoice, Select, MultiSelect, Spacer, Button
from bokeh.palettes import Turbo256#Category20

### TO DO
# - clear-all button for list selects
# - save current columns when switching month
# - drop NAs of each column on the fly so that lines actually get connected. I.E. different xs for each column
# - rearrange order of year-month 1...12
# - create empty data source upon start up, fill data when selecting in dropdown (necessary?)

# Create dict of input file paths
FILES = {}
DATADIR = "/data/isewer/data/012_split_by_year_month/by_month/"
for file in sorted(os.listdir(DATADIR)):
    if ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
        FILES[file[:7]] = DATADIR+file
INITIAL_FILE = "2022_04"

#new="2022_05"
### WIDGET CALLBACKS
def callback_new_data(attrname, old, new):
    print("updating data..")
    ### Load new data
    data = pd.read_feather(FILES[new])#columns=read_cols
    print("data loaded") 
    data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    source.data = data# use from_df?
    print("updated datasource")
    # update xlim of first plot (rest follows)
    ps[0].x_range.update(start=data.DateTime[0], end = data.DateTime[10000])
    print("updated plot limits")
    #plot_all(ps, source)#does not help

def callback_new_cols0 (attrname, old, new):
    # redraw plot 0 based on column selection
    cols = new + multi_list0.value
    draw_plot(ps[0], cols ,source,COLORS, ptype="circle")

def callback_new_cols1 (attrname, old, new):
    # redraw plot 2 based on columns selection
    cols = new + multi_list1.value
    draw_plot(ps[1], cols ,source,COLORS, ptype="bar")

def callback_multi_list0 (attrname, old, new):
    # add more cols to multichoice0.value & plot 0 redraw
    cols = multi_choice0.value + new
    draw_plot(ps[0], cols ,source,COLORS, ptype="circle")  

def callback_multi_list1 (attrname, old, new):
    # add more cols to multichoice1.value & plot 1 redraw
    cols = multi_choice1.value + new
    draw_plot(ps[1], cols ,source,COLORS, ptype="bar")  

def callback_button0():
    # empty multilist and replot only multicolumn selections
    multi_list0.value = []
    draw_plot(ps[0], multi_choice0.value ,source,COLORS, ptype="circle")

def callback_button1():
    # empty multilist and replot only multicolumn selections
    multi_list1.value = []
    draw_plot(ps[1], multi_choice1.value ,source,COLORS, ptype="bar")


### SET UP WIDGETS #1
### Dropdown to choose year
select0 = Select(title="Year/Month", value=INITIAL_FILE, options=list(FILES.keys()))#value=list(FILES.keys())[0]
select0.on_change("value",callback_new_data)

### CREATE DATASOURCE
data = pd.read_feather(FILES[select0.value])#columns=read_cols
print("data loaded") 
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
source = ColumnDataSource(data)
print("created datasource")
# save column names
all_cols = data.columns.to_list()
n_all_cols = len(all_cols)

### SET UP WIDGETS #2
### Choice of Variables to plot
#OPTIONS0 = ["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße","Niveau_RÜ_Hindenburgstraße","Niveau_RÜ_Vogesenstraße"]
mask0 = data.columns.str.contains("BerlinerAllee|Uferstraße|Hindenburgstraße|Vogesenstraße")
OPTIONS0 = sorted(data.columns[mask0 & data.columns.str.contains("Niveau")].to_list())
OPTIONS1 = sorted(data.columns[data.columns.str.contains("Niederschlag")].to_list()) + sorted(data.columns[mask0].to_list())

MULTI_LIST_WIDTH = 220
# Berliner Strang variables
multi_choice0 = MultiChoice(value=["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"], options=OPTIONS0)
multi_choice0.on_change("value", callback_new_cols0)
# NSM Variables
multi_choice1 = MultiChoice(value=["Niederschlag_Schwarzer_Steg", 'Niederschlag_Clara_Immerwahr_Straße', 'Niederschlag_Günterstal'], options=OPTIONS1)
multi_choice1.on_change("value", callback_new_cols1)
# Additional variables plot 1
multi_list0 =  MultiSelect(options=sorted(all_cols), title="Strg+Click to deselect", size=23, width=MULTI_LIST_WIDTH)
multi_list0.on_change("value", callback_multi_list0)
# Additional variables plot 2
multi_list1 =  MultiSelect(options=sorted(all_cols), size=23, width=MULTI_LIST_WIDTH)
multi_list1.on_change("value", callback_multi_list1)
# Emptying multilist0
button0 = Button(label="clear")
button0.on_event('button_click', callback_button0)

# Emptying multilist1
button1 = Button(label="clear")
button1.on_event('button_click', callback_button1)


### CREATE PLOTS
TOOLS = "pan,box_zoom,wheel_zoom,box_select,reset"
WIDTH, HEIGHT = 1500,350
# get one color for each variable
np.random.seed(12)#to keep colors the same
rand_seq = np.random.choice(n_all_cols,n_all_cols, replace=False)#randomize colors to get distiniguihsable colors from conitnous colormap
color_seq = [Turbo256[r] for r in rand_seq]
COLORS = dict(zip(all_cols,color_seq))

# Basic plot setup
ps = [[],[]]
xleft = data.DateTime[0]
xright = data.DateTime[10000]
ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS,x_range=(xleft,xright), active_drag="pan", active_scroll="wheel_zoom")
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS, x_range=ps[0].x_range)
# sizing to window
#ps[0].sizing_mode = 'scale_width'

# Additional tools:
tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
for p in ps:
    p.add_tools(HoverTool(tooltips=tooltips, mode='mouse', formatters={'@DateTime': 'datetime'}))

# Selection Bar at the bottom
slider = figure(height=100, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#
range_tool = RangeTool(x_range=ps[0].x_range)#
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

slider.circle(x='DateTime', size=3,y="Niveau_RÜ_BerlinerAllee",fill_color="darkgray",line_color=None, fill_alpha=0.7, source=source)#olors[0]
slider.ygrid.grid_line_color = None
slider.add_tools(range_tool)
slider.toolbar.active_multi = range_tool


### PLOTTING FUNCTIONS
def draw_plot(p, cols, source, COLORS, ptype):
    # Plots either one of the timeseries plots
    # ptype: "circle" or "bar", plotting type
    if p.legend: 
        p.legend.items = []
    p.renderers.clear()
    for col in cols:
        if ptype == "circle":
            p.circle(x='DateTime', y=col, size=3,
                            fill_color=COLORS[col], hover_fill_color="firebrick",
                            fill_alpha=0.7, hover_alpha=0.95,
                            line_color=None, hover_line_color="white", legend_label=col, name=col, source=source)
        if ptype == "bar":
            p.vbar(x='DateTime', top=col, width=2,
                fill_color=COLORS[col], fill_alpha=1, line_color=COLORS[col], legend_label=col, name=col, source=source)

#ottom, decorations, fill_alpha, fill_color, hatch_alpha, hatch_color, hatch_extra, hatch_pattern, hatch_scale, hatch_weight, js_event_callbacks, js_property_callbacks, line_alpha, line_cap, line_color, line_dash, line_dash_offset, line_join, line_width, name, subscribed_events, syncable, tags, top, width or x

def plot_all(ps, source):
    cols = [multi_choice0.value,multi_choice1.value]
    PTYPES = ["circle","bar"]
    for p_i in range(len(ps)):
        draw_plot(ps[p_i], cols[p_i],source,COLORS, ptype=PTYPES[p_i])
        ps[p_i].legend.location = "top_left"
        ps[p_i].legend.click_policy="hide"


# initial set-up
plot_all(ps, source)

### FILTERINGd
#view = CDSView(filter=IndexFilter([0, 2, 4]))
#p2.circle(x="x", y="y", size=10, hover_color="red", source=source, view=view)

# for obj in [ps[0], ps[1], select0, multi_list0,multi_choice0, select,multi_choice1]:
#     obj.sizing_mode = 'scale_both'
#layout.sizing_mode = 'scale_both'


# col0 = column(select0, multi_list0, multi_list1)
# col1 = column(multi_choice0, ps[0],multi_choice1, ps[1],slider)
# layout = row(col0, col1)


row0 = row(select0)
row1 = row(column(multi_list0, button0),column(multi_choice0, ps[0]))
row2 = row(column(multi_list1, button1),column(multi_choice1, ps[1]))
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
