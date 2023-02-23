import pandas as pd
import numpy as np

from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, RangeTool, CustomJS, MultiChoice
from bokeh.palettes import Category20
import itertools


### TO DO
# - drop NAs of each column on the fly so that lines actually get connected. I.E. different xs for each column

PATH_MWE = "/data/isewer/data/Prozessdaten_Acron_20220803.feather"

#read_cols = ["DateTime", "DaylightSavingTime"]+ col
data_raw = pd.read_feather(PATH_MWE)#columns=read_cols
# all_str = data_raw.columns.str.contains("_type")
# data_raw = data_raw.loc[:,~all_str]
print("data loaded") 


from bokeh.io import show
from bokeh.models import CustomJS, MultiChoice

OPTIONS0 = ["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße","Niveau_RÜ_Hindenburgstraße","Niveau_RÜ_Vogesenstraße"]
OPTIONS1 = data_raw.columns[data_raw.columns.str.contains("Niederschlag")].to_list()

# Berliner Strang variables
multi_choice0 = MultiChoice(value=["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"], options=OPTIONS0)
multi_choice0.js_on_change("value", CustomJS(code="""
    console.log('multi_choice: value=' + this.value, this.toString())
"""))
# NSM Variables
multi_choice1 = MultiChoice(value=OPTIONS1[:3], options=OPTIONS1)
multi_choice1.js_on_change("value", CustomJS(code="""
    console.log('multi_choice: value=' + this.value, this.toString())
"""))


#columns
cols = [multi_choice0.value,multi_choice1.value]
n_cols=[len(cols[0]),len(cols[1])]

# create subset, cols + Datetime
loadcols = [item for sublist in cols for item in sublist]
data = data_raw.loc[:,loadcols+["DateTime"]].dropna(how="all").copy()
#data = data_raw
data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"

# create color columns (as all has to be put into source)

colors = itertools.cycle(Category20[sum(n_cols)])
#colors = [["gray", "orange", "darkblue"],["gray", "orange", "darkblue"]]
# color_cols = [c+"_color" for c in cols]
# data[color_cols] = colors


#colors_seq = [np.repeat(c,len(data)) for c in colors]
#mypalette=Spectral11[0:n_cols]

#colors_seq = np.repeat(colors,len(data_raw),axis=)
# x = [data.DateTime.values]*n_cols
# y = [data[d].values for d in cols]

source = ColumnDataSource(data)
print("created datasource")

TOOLS = "pan,xpan,box_zoom,wheel_zoom,box_select,lasso_select,reset"
WIDTH, HEIGHT = 900,400
n_plots = 2
# Basic plot setup
#ps = [figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS) for i in range(n_plots)]
ps = [[],[]]
xleft = data.DateTime[0]
xright = data.DateTime[10000]
ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS,x_range=(xleft,xright))
ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS, x_range=ps[0].x_range, y_range=ps[0].y_range)


#p.multi_line(xs=x, ys=y, line_width=5, line_color=colors)
#p.multi_line(xs="DateTime", ys=cols, line_width=5, line_color=color_cols, source=source)

#p.multi_line(xs=x, ys=y, line_width=2)#, line_color=colors_seq
#p.line(x=stack('2016', '2017'), y='y', color='red',  source=source, name='2017')
# p.vline_stack(cols, x='DateTime', source=source)
# p1.vline_stack(cols1, x='DateTime', source=source)

crs = [[],[]]
for h in range(n_plots):
    ps[h].vline_stack(cols[h], x='DateTime', source=source)
    for i in range(n_cols[h]):
        cr = ps[h].circle(x='DateTime', y=cols[h][i], size=5,
                    fill_color=next(colors), hover_fill_color="firebrick",
                    fill_alpha=0.7, hover_alpha=0.95,
                    line_color=None, hover_line_color="white", legend_label=cols[h][i], name=cols[h][i], source=source)
        crs[h].append(cr)

    tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
    ps[h].add_tools(HoverTool(tooltips=tooltips, renderers=crs[h], mode='mouse', formatters={'@DateTime': 'datetime'}))
    ps[h].legend.location = "top_left"
    ps[h].legend.click_policy="hide"

select = figure(height=150, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#

range_tool = RangeTool(x_range=ps[0].x_range)#
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.circle(x='DateTime', size=5,y=cols[0][0],fill_color="darkgray",line_color=None, fill_alpha=0.7, source=source)#olors[0]
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

### FILTERING
#view = CDSView(filter=IndexFilter([0, 2, 4]))
#p2.circle(x="x", y="y", size=10, hover_color="red", source=source, view=view)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(multi_choice0, ps[0],multi_choice1, ps[1],select))




# import matplotlib.pyplot as plt
# ax = data.set_index("DateTime").loc[:,cols].plot(marker="o", linestyle='none', ms=1)
# ax.figure.savefig("test.png")
