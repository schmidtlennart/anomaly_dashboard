### WIDGET CALLBACKS

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from isewer_ast.plotting import draw_ts, draw_labels
from isewer_ast.helpers import create_data_source
from isewer_ast.plotting import plot_all

def wcb_select_voi(source, alldata, multi_list0, **kwargs):
    def cb_select_voi(attrname, old, new):
        nonlocal source, multi_list0
        # if not yet in dataset, load original data, add predictions and labels
        print(f"CHANGING VOI TO {new}")
        if new not in source.data.keys():
            newcols = [new] + ["pr_"+new] + ["pr_"+new+"_Label"]
            print("adding cols: \n")
            print(newcols)
            for nc in newcols:
                source.data[nc] = alldata[nc]
        multi_list0.value = [new] #triggers draw_ts
        #redraw labels
        print("REDRAWING LABELS")
        draw_labels(source=source,**kwargs)
    return cb_select_voi

def wcb_select_ym(FILES, FILES_PR, source, multi_list0, multi_list1, alldata, allcols,ps,slider,select_voi, **kwargs):
    def cb_select_ym(attrname, old, new):
        nonlocal FILES, FILES_PR, source, multi_list0, multi_list1,alldata, allcols, ps, slider,select_voi
        print(f"CHANGING TO YM {new},updating data..")
        # Assuming multi_list0.value, multi_list1.value, select_voi.value are lists
        current_cols = list(set(multi_list0.value + multi_list1.value + [select_voi.value]))
        # overwriting global objects
        source, alldata, allcols = create_data_source(FILES, FILES_PR, new, current_cols)

        # update xlim of first plot (rest follows)
        ps[0].x_range.update(start=alldata.DateTime[0], end = alldata.DateTime[5000])
        slider.x_range.update(start=alldata.DateTime.iloc[0], end = alldata.DateTime.iloc[-1])
        source.selected.indices = []
        print("PLOTTING ALL")
        plot_all(ps = ps, source=source, multi_list0=multi_list0, multi_list1=multi_list1,select_voi=select_voi, **kwargs)
        print("new head indices")
        print(source.data["DateTime"][:1])
    return cb_select_ym


def wcb_multi_list0(source, alldata, ps, **kwargs):
    def cb_multi_list0 (attrname, old, new):
        # inside closure, variables from parent scope (i.e. wrapper function) are read-only unless explicitly declared nonlocal
        # so set as nonlocal as I do want to change them in global scope
        nonlocal source
        print("UPDATING MULTILIST0 & REPLOTTING")
        # add respective columns to datasource
        newcols = list(set(new)-set(source.data.keys()))
        # add predictions too
        newcols = newcols + ["pr_"+c for c in newcols]
        print(f"Multilist selection: {new}")
        print("adding cols: \n")
        print(newcols)
        for nc in newcols:
            source.data[nc] = alldata[nc]
        draw_ts(p=ps[0], current_cols=new ,source=source, ptype="circle", **kwargs)
        print("DATA SOURCE:")
        print(pd.DataFrame(source.data).head())
    return cb_multi_list0

def wcb_multi_list1(source, alldata, ps, **kwargs):
    def cb_multi_list1 (attrname, old, new):
        nonlocal source
        print("UPDATING MULTILIST1 & REPLOTTING")
        # add respective columns to datasource (if not existant yet)
        newcols = list(set(new)-set(source.data.keys()))
        # add predictions too
        newcols = newcols + ["pr_"+c for c in newcols]
        print("adding cols: \n")
        print(newcols)
        for nc in newcols:
            source.data[nc] = alldata[nc]
        #redraw
        draw_ts(p=ps[1], current_cols=new ,source=source, ptype="bar",**kwargs)
    return cb_multi_list1

# Multlist for anomaly events from ae
def wcb_multi_list_ae(anomalies_df, select_voi, select_ym, ps, **kwargs):
    def cb_multi_list_ae(attrname, old, new):
        nonlocal anomalies_df
        print("UPDATING MULTILIST_AE")
        print(new)
        event = anomalies_df.loc[anomalies_df["multi"].isin(new), :]
        print(event)
        # update select_ym and select_voi        
        if event["variable"].to_list() != select_voi.value:
            select_voi.value = str(event["variable"].iloc[0])# triggers redraw (...)
        if event["Y_M"].to_list() != select_ym.value:
            select_ym.value = str(event["Y_M"].iloc[0])# also triggers redraw

        # update xlim of first plot (rest follows)
        ps[0].x_range.update(start=event["start"].iloc[0], end = event["end"].iloc[0])
    return cb_multi_list_ae

# Multlist for manual labels
def wcb_multi_list_manual(anomalies_df_manual, select_voi, select_ym, ps, **kwargs):
    def cb_multi_list_manual(attrname, old, new):
        nonlocal anomalies_df_manual
        print("UPDATING MULTILIST_MANUAL")
        print(new)
        event = anomalies_df_manual.loc[anomalies_df_manual["multi"].isin(new), :]
        print(event)
        # update select_ym and select_voi        
        if event["variable"].to_list() != select_voi.value:
            select_voi.value = str(event["variable"].iloc[0])# triggers redraw (...)
        if event["Y_M"].to_list() != select_ym.value:
            select_ym.value = str(event["Y_M"].iloc[0])# also triggers redraw

        # update xlim of first plot (rest follows)
        ps[0].x_range.update(start=event["start"].iloc[0], end = event["end"].iloc[0])
    return cb_multi_list_manual

def wcb_clearbutton0(multi_list0):
    def cb_clearbutton0():
        nonlocal multi_list0
        # empty multilist and replot only multicolumn selections
        multi_list0.value = []
    return cb_clearbutton0

def wcb_clearbutton1(multi_list1):
    def cb_clearbutton1():
        nonlocal multi_list1
        # empty multilist and replot only multicolumn selections
        multi_list1.value = []
    return cb_clearbutton1

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
