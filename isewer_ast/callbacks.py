### WIDGET CALLBACKS
# change month to be plotted

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from isewer_ast.plotting import draw_ts, draw_labels, plot_all, create_colors

def cb_select_voi(attrname, old, new):
    # if not yet in dataset, load original data, add predictions and labels
    if new not in source.data.keys():
        newcols = [new] + ["pr_"+new] + ["pr_"+new+"_Label"]
        print("adding cols: \n")
        print(newcols)
        for nc in newcols:
            source.data[nc] = alldata[nc]

    # redraw plot 0 based on column selection to change visual selection behaviour as voi changes
    cols = multi_list0.value + multi_choice0.value + [new]
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
    #predictions
    data_pr = pd.read_feather(FILES_PR[new])#columns=read_cols
    print("data_pr loaded") 
    #data_pr.DateTime = pd.to_datetime(data_pr.DateTime)# no need to set format because done in "011_load_to_feather.py"
    
    ################# TEMPORARY FIX FOR DATETIME
    #data_pr["DateTime"] = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    ################# !!!!
    data_pr.columns = ["pr_"+c for c in data_pr.columns]
    # recode labels 0 to np.nan forplotting
    data_pr_plot = data_pr.copy()
    data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")] = data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")].replace({0:np.nan})

    cols0 = INITIALCOLS + multi_list0.value + multi_list1.value
    cols_pr = ["pr_"+c for c in cols0] + ["pr_"+c+"_Label" for c in cols0]
    # drop if "pr_DateTime_Label"
    cols_pr = [c for c in cols_pr if not c=="pr_DateTime_Label"]
    #add labels from predictions
    alldata = pd.concat([data,data_pr_plot], axis=1)
    source.data = alldata.loc[:,cols0+cols_pr].copy()
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
   
def wcb_new_cols0 (multi_list0, ps, **kwargs):
    # callback is only allowed these three positional arguments but I need more so wrap
    def cb_new_cols0(attrname, old, new):
        # redraw plot 0 based on column selection
        cols = new + multi_list0.value
        draw_ts(p=ps[0], cols=cols, ptype="circle", **kwargs)
    return cb_new_cols0

# def wcb_new_cols0(attr, old, new):
#     cb_new_cols0(attr, old, new, **kwargs)
def wcb_new_cols1(multi_list1,ps,**kwargs):
    def cb_new_cols1 (attrname, old, new):
        # redraw plot 2 based on columns selection
        cols = new + multi_list1.value
        draw_ts(ps[1], cols, ptype="bar", **kwargs)
    return cb_new_cols1


def cb_multi_list0 (attrname, old, new,):
    # add respective columns to datasource
    newcols = list(set(new)-set(source.data.keys()))
    # add predictions too
    newcols = newcols + ["pr_"+c for c in newcols]
    print("adding cols: \n")
    print(newcols)
    for nc in newcols:
        source.data[nc] = alldata[nc]
    # add all cols from this list to multichoice0.value & plot 0 redraw
    cols = multi_choice0.value + new
    draw_ts(ps[0], cols ,source,COLORS, ptype="circle")  

def cb_multi_list1 (attrname, old, new):
    # add respective columns to datasource (if not existant yet)
    # add respective columns to datasource
    newcols = list(set(new)-set(source.data.keys()))
    # add predictions too
    newcols = newcols + ["pr_"+c for c in newcols]
    print("adding cols: \n")
    print(newcols)
    for nc in newcols:
        source.data[nc] = alldata[nc]    # add all cols from this list to multichoice1.value & plot 1 redraw
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
    outdata = source.to_df().copy()
    outdata = outdata.loc[:,outdata.columns.str.contains("_Label")]
    data.loc[:,outdata.columns] = outdata.copy()
    ym = old if old else select_ym.value
    print(f"Old from selection: {old}")
    print(f"Saving to: {ym}")
    print("Data indices")
    print(data.DateTime[:1])### HIER HAT ER IMMER NOCH APRIL, aber irgwie nur in dieser Funktion
    data.to_feather(FILES[ym])
    print("saved data")



