import pandas as pd
import numpy as np

from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, RangeTool, CustomJS, MultiChoice
from bokeh.palettes import Viridis256#Category20

### TO DO
# - drop NAs of each column on the fly so that lines actually get connected. I.E. different xs for each column

## TWO WAYS To ACHIEVE DROP DOWN:
# - clean renderers entirely and re-plot in callback
# - Preferred: create renderer list for all columns, fill/empty those that change
# - create all plots, toggle visibility in callback


### LOAD DATA
# all cols available in plot
# loadcols = OPTIONS0 + OPTIONS1 + ["DateTime"]
PATH = "/data/isewer/data/012_split_by_year_month/2021_05_Prozessdaten_Acron_20220803.feather"
data_raw = pd.read_feather(PATH)#columns=read_cols
print("data loaded") 
data = data_raw
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
source = ColumnDataSource(data)
print("created datasource")
# save column names
all_cols = data.columns.values
n_all_cols = len(all_cols)


### WIDGET CALLBACKS
def callback0 (attrname, old, new):
 update_plot(ps[0], new ,source,COLORS)

def callback1 (attrname, old, new):
 update_plot(ps[1], new ,source,COLORS)

### SET UP WIDGETS
OPTIONS0 = ["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße","Niveau_RÜ_Hindenburgstraße","Niveau_RÜ_Vogesenstraße"]
OPTIONS1 = data.columns[data.columns.str.contains("Niederschlag")].to_list()
# Berliner Strang variables
multi_choice0 = MultiChoice(value=["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"], options=OPTIONS0)
multi_choice0.on_change("value", callback0)
# NSM Variables
multi_choice1 = MultiChoice(value=OPTIONS1[:3], options=OPTIONS1)
multi_choice1.on_change("value", callback1)


### CREATE PLOTS
TOOLS = "pan,xpan,box_zoom,wheel_zoom,box_select,lasso_select,reset"
WIDTH, HEIGHT = 1500,350
# get one color for each variable
COLORS = dict(zip(all_cols,Viridis256[:n_all_cols]))

# Basic plot setup
ps = [[],[]]
xleft = data.DateTime[0]
xright = data.DateTime[10000]
ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS,x_range=(xleft,xright), active_drag="pan", active_scroll="wheel_zoom")
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS, x_range=ps[0].x_range, y_range=ps[0].y_range)
# Additional tools:
tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
for p in ps:
    p.add_tools(HoverTool(tooltips=tooltips, mode='mouse', formatters={'@DateTime': 'datetime'}))

# Selection Bar at the bottom
select = figure(height=100, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#
range_tool = RangeTool(x_range=ps[0].x_range)#
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.circle(x='DateTime', size=5,y="Niveau_RÜ_BerlinerAllee",fill_color="darkgray",line_color=None, fill_alpha=0.7, source=source)#olors[0]
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool


def update_plot(p, cols, source, COLORS):
    # OLD
    # collect existing renderers by name
    # renderer_names = [r.name for r in p.renderers]
    # names_keep = set(cols) - set(renderer_names)
    # names_add = set(cols)-names_keep

    # renderer_names_s = pd.Series([r.name for r in p.renderers])
    # cols_s = pd.Series(cols)
    # # keep only the ones still needed
    # indices_keep = renderer_names_s[renderer_names_s.isin(cols)].index.values   
    # new_renderers=[]  
    # for ind in indices_keep:
    #     new_renderers.append(p.renderers[ind]) 
    # p.renderers = new_renderers
    # # draw new ones
    # cols_add = cols_s[~cols_s.isin(renderer_names_s)]
    # for col in cols_add:
    #     p.circle(x='DateTime', y=col, size=5,
    #                     fill_color=COLORS[col], hover_fill_color="firebrick",
    #                     fill_alpha=0.7, hover_alpha=0.95,
    #                     line_color=None, hover_line_color="white", legend_label=col, name=col, source=source)

    #p.renderers = []# There is also: plot.renderers.remove(line)
    p.legend.items = []
    p.renderers.clear()
    for col in cols:
        p.circle(x='DateTime', y=col, size=5,
                        fill_color=COLORS[col], hover_fill_color="firebrick",
                        fill_alpha=0.7, hover_alpha=0.95,
                        line_color=None, hover_line_color="white", legend_label=col, name=col, source=source)

# initial set-up
cols = [multi_choice0.value,multi_choice1.value]
for p_i in range(len(ps)):
    update_plot(ps[p_i], cols[p_i],source,COLORS)
    ps[p_i].legend.location = "top_left"
    ps[p_i].legend.click_policy="hide"

### FILTERINGd
#view = CDSView(filter=IndexFilter([0, 2, 4]))
#p2.circle(x="x", y="y", size=10, hover_color="red", source=source, view=view)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(multi_choice0, ps[0],multi_choice1, ps[1],select))
curdoc().title = "i-SEWER Anomaly Selection Tool"

#ps[0].legend.items.clear()
### UPDATE DATA SOURCE WHEN CHOOSING OTHER MONTH
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
