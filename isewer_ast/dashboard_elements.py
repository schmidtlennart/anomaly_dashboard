from bokeh.plotting import figure
from bokeh.models import RangeTool, HoverTool, Select, MultiSelect, MultiChoice, Button, RadioButtonGroup

from isewer_ast.constants import *

def create_plot_objects(data, current_voi):
    # Basic plot setup
    ps = [[],[]]#holds timeseries
    xleft = data.DateTime[0]
    xright = data.DateTime[10000]
    ps[0] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS0,x_range=(xleft,xright), active_drag="pan", active_scroll="ywheel_zoom")#, output_backend="webgl"#webgl=GPU acceleration, causes problems with vbar
    ps[1] = figure(width=WIDTH, height=HEIGHT, x_axis_type="datetime", title='',tools=TOOLS1, x_range=ps[0].x_range)
    # holds labels
    pl = figure(width=WIDTH, height=HEIGHT1, x_axis_type="datetime", title='',tools="box_select",toolbar_location=None, y_axis_type=None,x_range=ps[0].x_range, y_range=(0,1), active_drag="box_select")
    pl.ygrid.grid_line_color = None

    # Additional tools (does not work for barchart, so only ps0)
    tooltips = [("Name","$name"),("Value","$y"),("DateTime", "@DateTime{%F %T}")]
    hover = HoverTool(tooltips=tooltips, mode='mouse', formatters={'@DateTime': 'datetime'})
    ps[0].add_tools(hover)

    # Selection Bar at the bottom
    slider = figure(height=HEIGHT1, width=WIDTH, x_axis_type="datetime", title="", y_axis_type=None, tools="", toolbar_location=None)#
    range_tool = RangeTool(x_range=ps[0].x_range)#
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2
    slider.circle(x='DateTime', size=3,y=current_voi,fill_color="darkgray",line_color=None, fill_alpha=0.7, source=source)#olors[0]
    slider.ygrid.grid_line_color = None
    slider.add_tools(range_tool)
    #slider.toolbar.active_multi = range_tool
    return ps, pl, slider

def create_widgets(FILES, all_cols, INITAL_COLS0, INITIAL_COLS1):
    # Set up widgets
    # Selector: Year/Month
    select_ym = Select(title="Year/Month", value=INITIAL_FILE, options=list(FILES.keys()))#value=list(FILES.keys())[0]
    # Selector: Variable of Interest
    select_voi = Select(title="Variable of Interest", value=INITIAL_VOI, options=sorted(all_cols))#, options=OPTIONS0)
    # Additional variables plot 1
    multi_list0 =  MultiSelect(options=sorted(all_cols), value=INITAL_COLS0, title="Strg+Click to deselect", size=23, width=MULTI_LIST_WIDTH)
    # Additional variables plot 2
    multi_list1 =  MultiSelect(options=sorted(all_cols), value=INITIAL_COLS1, size=23, width=MULTI_LIST_WIDTH)
    return select_ym,select_voi, multi_list0, multi_list1

def create_buttons():
    # Emptying multilist0
    clearbutton0 = Button(label="clear")
    # Emptying multilist1
    clearbutton1 = Button(label="clear")
    ### LABELLING
    # Anomaly Label buttons, Set label if pressed
    label_buttons = RadioButtonGroup(labels=LABELS, button_type="primary",disabled=True, width=1500, height=35)
    # delete labels in current selection
    button_delete_sel_labels = Button(label="Delete labels in selection", button_type="danger", height=35, width=500,disabled=True)

    #delete all labels that were set
    button_delete_all_labels = Button(label="Delete all labels", button_type="danger", height=25)
    # save all labels to feather-file
    button_save_all_labels = Button(label="Save labels to file", button_type="success", height=25)
    return clearbutton0, clearbutton1, label_buttons, button_delete_sel_labels, button_delete_all_labels, button_save_all_labels
