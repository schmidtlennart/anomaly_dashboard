from bokeh.layouts import column
from bokeh.models import Button
from bokeh.plotting import curdoc, figure

p = figure(tools="reset,pan,wheel_zoom,lasso_select")
p.circle(list(range(10)), list(range(10)), legend_label="a", name="a")

def clear_plot(attr):
    p.renderers = []
    p.circle(list(range(20)), list(range(20)), legend_label="b", name="b")
    p.circle(list(range(5)), list(range(5)), color="red", legend_label="c", name="c")


b = Button(label="Clear plot")
b.on_click(clear_plot)

curdoc().add_root(column(p, b))