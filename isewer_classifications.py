### FIXING DATA SAVING BUG
# .copy()
# bokeh source.update_DataSource o.ä.
# print source.data vs. outdata vs data

##TODO:
# fix zooming: resetting, separate x&y zooming/manual
# fix resetting after YM change
# OPTIONAL:
# update slider inside drawing functions as well

import pandas as pd
# pd n columns shown
pd.set_option('display.max_columns', 500)
import numpy as np
from bokeh.plotting import curdoc
from bokeh.layouts import column, row
from bokeh.models import Spacer

from isewer_ast.callbacks import *
from isewer_ast.constants import *
from isewer_ast.helpers import get_filenames, create_data_source, load_anomalies
from isewer_ast.plotting import create_colors, plot_all
from isewer_ast.dashboard_elements import create_plot_objects, create_widgets, create_buttons

################## CREATE DATASOURCE & GET RELEVANT COLUMNS, COLORS #############################
# read montly input file names

FILES, FILES_PR = [get_filenames(f) for f in [DATADIR, DATADIR_CL]]

source, alldata, allcols = create_data_source(FILES, FILES_PR, INITIAL_FILE, [INITIAL_COLS0, INITIAL_COLS1])
anomalies_df = load_anomalies(PATH_AE_ANOMALIES, filter=True)
anomalies_df_manual = load_anomalies(PATH_AE_ANOMALIES_MANUAL, filter=False)
# create colors for all columns
COLORS = create_colors(alldata.columns.to_list())

#anomalies_df = pd.read_feather(PATH_AE_ANOMALIES).sort_values(by="length", ascending=False)
#d = anomalies_df.loc[anomalies_df.loc[:,"variable"]=="Niveau_Radar_RÜ_Sundgauallee",:]

################## WIDGETS & BUTTONS #############################
select_ym, select_voi, multi_list0, multi_list1, multi_list_ae, multi_list_manual = create_widgets(FILES, allcols, anomalies_df["multi"].to_list(), anomalies_df_manual["multi"].to_list())
clearbutton0, clearbutton1, label_buttons, button_delete_sel_labels, button_delete_all_labels, button_save_all_labels = create_buttons()

################## PLOTS #############################
ps, pl, slider = create_plot_objects(alldata, select_voi, source)

################## CALLBACKS ################## 
# All objects needed in callbacks
# TO DO: Turn into class object that I can simply pass around (=only one kw argument)
args = {"FILES":FILES, "FILES_PR":FILES_PR, "source": source, "alldata":alldata, "allcols":allcols, "COLORS": COLORS, "ps": ps, "pl":pl, "slider":slider,"select_voi":select_voi, "multi_list0":multi_list0, "multi_list1":multi_list1, "multi_list_ae":multi_list_ae, "multi_list_manual":multi_list_manual, "anomalies_df":anomalies_df, "anomalies_df_manual":anomalies_df_manual,"select_ym":select_ym}

# Labelling actions only allowed if data is selected
source.selected.on_change('indices', wcb_selection_change(label_buttons, button_delete_sel_labels))
# data and column selectors
select_ym.on_change("value",wcb_select_ym(**args))#change of month
select_voi.on_change("value", wcb_select_voi(**args))#change of Variable of Interest
multi_list0.on_change("value", wcb_multi_list0(**args))# change of selection in multilist0
multi_list1.on_change("value", wcb_multi_list1(**args))# change of selection in multilist1
multi_list_ae.on_change("value", wcb_multi_list_ae(**args))# change of anomaly event
multi_list_manual.on_change("value", wcb_multi_list_manual(**args))# change of anomaly event

# Button Callbacks
clearbutton0.on_event('button_click', wcb_clearbutton0(multi_list0=multi_list0))
clearbutton1.on_event('button_click', wcb_clearbutton1(multi_list1=multi_list1))
#label_buttons.on_change("active", cb_set_labels)
# button_delete_sel_labels.on_event('button_click', cb_delete_sel_labels)
# button_delete_all_labels.on_event('button_click', cb_delete_all_labels)
# button_save_all_labels.on_event('button_click', cb_save_all_labels)

#################### PLOT & DASHBOARD LAYOUT ####################
plot_all(**args)

row0 = row(select_ym,select_voi)
#row01 = row(label_buttons, button_delete_sel_labels)
row1 = row(column(multi_list0, clearbutton0),column(ps[0],pl))# button_delete_all_labels, button_save_all_labels
row2 = row(column(multi_list1, clearbutton1),column(ps[1]))
row2_1 = row(row1, multi_list_ae)
row2_2 = row(row2, multi_list_manual)
row3 = row(Spacer(width=MULTI_LIST_WIDTH),slider)
layout=column(row0, row2_1,row2_2,row3)
curdoc().add_root(layout)
curdoc().title = "i-SEWER Classifications"
