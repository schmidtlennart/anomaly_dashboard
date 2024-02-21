import os, random
import numpy as np
from bokeh.palettes import Turbo256
from bokeh.transform import linear_cmap

from isewer_ast.constants import LABELS, LABELCOLORS
from bokeh.models import Legend, LegendItem

# make sure Colors are only assigned once (used to be run multiple times when it was was sill inside main script)
# Initialize COLORS to None at the module level
COLORS = None
def create_colors(all_cols):
    global COLORS
    # If COLORS is already set, return it
    if COLORS is not None:
        return COLORS

    # get one color for each variable
    seed = 36
    # 1. Set `PYTHONHASHSEED` environment variable at a fixed value
    os.environ['PYTHONHASHSEED']=str(seed)
    random.seed(seed)
    np.random.seed(seed)  # to keep colors the same
    n_all_cols = len(all_cols)
    rand_seq = np.random.choice(n_all_cols, n_all_cols, replace=False)  # randomize colors to get distinguishable colors from continuous colormap
    palette = Turbo256*4  # more than 256 variables
    color_seq = [palette[r] for r in rand_seq]
    COLORS = dict(zip(all_cols, color_seq))
    return COLORS


### PLOTTING FUNCTIONS
def draw_ts(source, COLORS,p, current_cols, ptype, current_voi,**kwargs):
    # Plots either one of the timeseries plots
    # ptype: "circle" or "bar", plotting type
    plotcols = current_cols + ["pr_"+c for c in current_cols]
    if p.legend: 
        p.legend.items = []
    #clear plot
    p.renderers = []#.clear()
    # top plot: circles
    if ptype == "circle":
        for col in plotcols:
            nonselect_alpha = 1
            select_color = COLORS[col]
            size=3
            # if col = voi enable changing appearance of points
            if col == current_voi:
                nonselect_alpha = 1
                select_color = "orange"
                size = 3
            p.circle(x='DateTime', y=col, size=size,
                            fill_color=COLORS[col], hover_fill_color="firebrick",
                            fill_alpha=1, hover_alpha=0.95,
                            line_color=None, hover_line_color="white", legend_label=col, name=col, source=source, nonselection_fill_alpha=nonselect_alpha,
                            selection_color=select_color)
    #bottom plot: bars
    if ptype == "bar":
        for col in plotcols:
            p.vbar(x='DateTime', top=col, width=2,
                fill_color=COLORS[col], fill_alpha=1, line_color=COLORS[col], legend_label=col, name=col, source=source, nonselection_fill_alpha=1)# somehow non-selection alpha does not work

def draw_labels(pl, source, current_voi, **kwargs):
    if pl.legend: 
        pl.legend.items = []
    pl.renderers.clear()
    var = "pr_"+current_voi+"_Label"
    cmap = linear_cmap(field_name=var, palette=LABELCOLORS, low=0.1, high=1)
    pl.rect(x='DateTime', y=var, width=80000, height=4, source=source,#size=16
        fill_alpha=1, fill_color=cmap,line_color=None,#,#"color"
                selection_color="orange")
    print("added label circles")
    # Hacky custom label legend these are a dummy glyphs to help draw the legend
    dummy_rs = [pl.circle(x=[0, 0], y=[0, 0], line_width=1, color=c,line_color=None, name='dummy_for_legend') for c in LABELCOLORS]
    legend = Legend(items=[LegendItem(label=l, renderers=[r]) for l,r in zip(LABELS,dummy_rs)],
        location="top_right", orientation="horizontal",
        border_line_color=None)
    pl.add_layout(legend)

def plot_all(ps, pl, current_cols0, current_cols1, **kwargs):
    # observed cols + predicted ones
    cols = [current_cols0, current_cols1]
    PTYPES = ["circle","bar"]
    for p_i in range(len(ps)):
        draw_ts(p=ps[p_i], current_cols= cols[p_i], ptype=PTYPES[p_i], **kwargs)
        ps[p_i].legend.location = "top_left"
        ps[p_i].legend.click_policy="hide"
    draw_labels(pl=pl, **kwargs)
    pl.legend.orientation = "horizontal"
    pl.legend.location = "top_right"
    pl.legend.border_line_color = None
