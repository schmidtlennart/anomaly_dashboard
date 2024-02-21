### WIDGET CALLBACKS

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from isewer_ast.plotting import create_colors, draw_ts, draw_labels

def wcb_select_voi(source, alldata, ps, current_cols0, current_voi, **kwargs):
    def cb_select_voi(attrname, old, new):
        nonlocal source, current_cols0, current_voi
        # if not yet in dataset, load original data, add predictions and labels
        if new not in source.data.keys():
            newcols = [new] + ["pr_"+new] + ["pr_"+new+"_Label"]
            print("adding cols: \n")
            print(newcols)
            for nc in newcols:
                source.data[nc] = alldata[nc]

        # update allcols0
        current_cols0 = current_cols0 + [new]
        current_voi = new# overwrite for global scope

        # redraw plot 0 based on column selection to change visual selection behaviour as voi changes
        draw_ts(p=ps[0], current_cols=current_cols0, source=source, current_voi=current_voi, ptype="circle", **kwargs)
        #redraw labels
        draw_labels(current_voi=current_voi, source=source,**kwargs)
    return cb_select_voi


# def cb_new_data(attrname, old, new):
#     print("updating data..")
#     ### save current data to file
#     print(f"old: {old}")
#     print(f"new: {new}")
#     #cb_save_all_labels(old)
#     ### Load new data
#     data = pd.read_feather(FILES[new])#columns=read_cols
#     print("data loaded") 
#     data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
#     #predictions
#     data_pr = pd.read_feather(FILES_PR[new])#columns=read_cols
#     print("data_pr loaded") 
#     #data_pr.DateTime = pd.to_datetime(data_pr.DateTime)# no need to set format because done in "011_load_to_feather.py"
    
#     ################# TEMPORARY FIX FOR DATETIME
#     #data_pr["DateTime"] = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
#     ################# !!!!
#     data_pr.columns = ["pr_"+c for c in data_pr.columns]
#     # recode labels 0 to np.nan forplotting
#     data_pr_plot = data_pr.copy()
#     data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")] = data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")].replace({0:np.nan})

#     cols0 = INITIALCOLS + multi_list0.value + multi_list1.value
#     cols_pr = ["pr_"+c for c in cols0] + ["pr_"+c+"_Label" for c in cols0]
#     # drop if "pr_DateTime_Label"
#     cols_pr = [c for c in cols_pr if not c=="pr_DateTime_Label"]
#     #add labels from predictions
#     alldata = pd.concat([data,data_pr_plot], axis=1)
#     source.data = alldata.loc[:,cols0+cols_pr].copy()
#     print("updated datasource")
#     # update xlim of first plot (rest follows)
#     ps[0].x_range.update(start=data.DateTime[0], end = data.DateTime[10000])
#     #print("updated plot limits")
#     source.selected.indices = []
#     #print("cleared selection")
#     plot_all(ps, source)
#     print("new head indices")
#     print(source.data["DateTime"][:1])
#     print("Data indices")
#     print(data.DateTime[:1])


def wcb_multi_list0(source, alldata, ps, current_cols0, **kwargs):
    def cb_multi_list0 (attrname, old, new,):
        # inside closure, variables from parent scope (i.e. wrapper function) are read-only unless explicitly declared nonlocal
        # so set as nonlocal as I do want to change them in global scope
        nonlocal source, current_cols0
        # add respective columns to datasource
        newcols = list(set(new)-set(source.data.keys()))
        # add predictions too
        newcols = newcols + ["pr_"+c for c in newcols]
        print("adding cols: \n")
        print(newcols)
        for nc in newcols:
            source.data[nc] = alldata[nc]
        # add all cols from this list to multichoice0.value & plot 0 redraw
        # changed here but reflects in global scope
        current_cols0 = new
        draw_ts(p=ps[0], current_cols=current_cols0 ,source=source, ptype="circle", **kwargs)
    return cb_multi_list0

def wcb_multi_list1(source, alldata, ps, current_cols1, **kwargs):
    def cb_multi_list1 (attrname, old, new):
        nonlocal source, current_cols1
        # add respective columns to datasource (if not existant yet)
        newcols = list(set(new)-set(source.data.keys()))
        # add predictions too
        newcols = newcols + ["pr_"+c for c in newcols]
        print("adding cols: \n")
        print(newcols)
        for nc in newcols:
            source.data[nc] = alldata[nc]    # add all cols from this list to multichoice1.value & plot 1 redraw
        current_cols1 = new
        draw_ts(p=ps[1], current_cols=current_cols1 ,source=source, ptype="bar",**kwargs)
    return cb_multi_list1

def cb_clearbutton0(multi_list0):
    # empty multilist and replot only multicolumn selections
    multi_list0.value = []
    # is this really needed? shoud trigger .on_change cb
    #draw_ts(ps[0], cols=[],source,COLORS, ptype="circle")

def cb_clearbutton1(multi_list1):
    # empty multilist and replot only multicolumn selections
    multi_list1.value = []
    #draw_ts(ps[1], multi_choice1.value ,source,COLORS, ptype="bar")

def wcb_selection_change(label_buttons, button_delete_sel_labels, **kwargs):
    def cb_selection_change (attrname, old, new):
            label_buttons.disabled=False
            button_delete_sel_labels.disabled=False
    return cb_selection_change

### LABELLING
# after selection of anomalous data, save flag into data
# def cb_set_labels(attrname, old, new):
#     #print(new)
#     voi_label = select_voi.value + "_Label"
#     selected = source.selected.indices
#     if selected:
#         patch = {voi_label : [(s,(new+1)/10) for s in selected]}#NaN =No Label, >0 = one of the labels
#         #print(patch)
#         source.patch(patch)
#         print("patched datasource")
#     # after operation, reset selected indices + buttons
#     source.selected.indices = []
#     label_buttons.active = None
#     label_buttons.disabled=True
#     button_delete_sel_labels.disabled=True
# # delte labels in selection
# def cb_delete_sel_labels():
#     voi_label = select_voi.value + "_Label"
#     selected = source.selected.indices
#     if selected:
#         #NaN =No Label, >0 = one of the labels, either 0.1,0.2 or 0.3. +1 for values starting with 1 / 10 = 0.1
#         patch = {voi_label : [(s,np.nan) for s in selected]}
#         source.patch(patch)
#     # after operation, reset selected indices + buttons
#     source.selected.indices = []
#     label_buttons.active = None
#     label_buttons.disabled=True
#     button_delete_sel_labels.disabled=True
# # delete all labels of current month
# def cb_delete_all_labels():
#     voi_label = select_voi.value + "_Label"
#     source.data[voi_label] = np.repeat(np.nan, len(source.data[voi_label]))
# # save all labels of current month to feather-file
# def cb_save_all_labels(old=None):
#     # old: if called via cb_select_ym, save old data using old ym
#     outdata = source.to_df().copy()
#     outdata = outdata.loc[:,outdata.columns.str.contains("_Label")]
#     data.loc[:,outdata.columns] = outdata.copy()
#     ym = old if old else select_ym.value
#     print(f"Old from selection: {old}")
#     print(f"Saving to: {ym}")
#     print("Data indices")
#     print(data.DateTime[:1])### HIER HAT ER IMMER NOCH APRIL, aber irgwie nur in dieser Funktion
#     data.to_feather(FILES[ym])
#     print("saved data")



