

### WIDGET CALLBACKS
def cb_new_data(attrname, old, new):
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

def cb_new_cols0 (attrname, old, new):
    # redraw plot 0 based on column selection
    cols = new + multi_list0.value
    draw_plot(ps[0], cols ,source,COLORS, ptype="circle")

def cb_new_cols1 (attrname, old, new):
    # redraw plot 2 based on columns selection
    cols = new + multi_list1.value
    draw_plot(ps[1], cols ,source,COLORS, ptype="bar")

def cb_multi_list0 (attrname, old, new):
    # add more cols to multichoice0.value & plot 0 redraw
    cols = multi_choice0.value + new
    draw_plot(ps[0], cols ,source,COLORS, ptype="circle")  

def cb_multi_list1 (attrname, old, new):
    # add more cols to multichoice1.value & plot 1 redraw
    cols = multi_choice1.value + new
    draw_plot(ps[1], cols ,source,COLORS, ptype="bar")  

def cb_button0():
    # empty multilist and replot only multicolumn selections
    multi_list0.value = []
    draw_plot(ps[0], multi_choice0.value ,source,COLORS, ptype="circle")

def cb_button1():
    # empty multilist and replot only multicolumn selections
    multi_list1.value = []
    draw_plot(ps[1], multi_choice1.value ,source,COLORS, ptype="bar")

def cb_selection_change (attrname, old, new):
        selected = source.selected.indices
    # if selected:
    #     data = data.iloc[selected, :]