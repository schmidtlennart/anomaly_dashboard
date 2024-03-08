import os
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from isewer_ast.constants import PATH_AE_ANOMALIES, N_AE_ANOMALIES, FILTER_ANOMALIES

def get_filenames(dir):
    # Create dict of input file paths
    FILES = {}
    for file in sorted(os.listdir(dir)):
        if ("2024_" in file) | ("2023_" in file) | ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
            FILES[file[:7]] = dir+file
    return FILES

def columns_to_pr_label(cols, keeporiginal=True):
    # if list of lists, flatten
    if isinstance(cols[0], list):
        cols = [item for sublist in cols for item in sublist]
   # turn columns into labels, predictions and their labels
    pr = ["pr_"+c for c in cols]
    label = ["pr_"+c+"_Label" for c in cols]
    if keeporiginal:
        return cols+pr+label
    else:
        return pr+label

def create_data_source(FILES, FILES_PR, file, current_cols):
    # observed
    data = pd.read_feather(FILES[file])#columns=read_cols
    print("data loaded") 
    data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    # predictions
    data_pr = pd.read_feather(FILES_PR[file])#columns=read_cols
    
    print("data_pr loaded") 
    # drop label columns in data (if existant)
    data = data.loc[:,~data.columns.str.contains("_Label")]
    # reduce both to the inner join set of columns, i.e. also remove labels (might be existant in both)
    cols_joint = list(set(data.columns.to_list())& set(data_pr.columns.to_list()))
    # remove Month, Year, index, DateTime (as there are no Labels for this)
    cols_joint = [c for c in cols_joint if c not in ["Month","Year","index", "DateTime"]]
    data = data.loc[:,["DateTime"] + cols_joint]
    # add pr_ to columns of predictions
    data_pr.columns = ["pr_"+c for c in data_pr.columns]
    # select joint columns but with pr_ and _Label
    data_pr = data_pr.loc[:,columns_to_pr_label(cols_joint,keeporiginal=False)]
    # recode labels 0 -> np.nan forplotting
    data_pr_plot = data_pr.copy()
    data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")] = data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")].replace({0:np.nan})

    ### merge predictions and observed data
    alldata = pd.concat([data,data_pr_plot], axis=1)

    load_cols = ["DateTime"] + columns_to_pr_label(current_cols)
    source = ColumnDataSource(alldata.loc[:,load_cols])
    print("(re-)created datasource")
    # return data source, alldata (i.e. data, pr_data and pr_labels) and all data columns (for col selection so withour _pr or _Label)
    return source, alldata, data.columns.to_list()

def load_anomalies(path,filter=False):
    # load ae-anomalies
    ae_event_df = pd.read_feather(path).sort_values(by="length", ascending=False).head(N_AE_ANOMALIES)
    if filter:
        # filter for niveau, not at NORD or SK
        mask = (ae_event_df["variable"].str.contains("Niveau")) & (~ae_event_df["variable"].str.contains("Nord|SK"))
        #ae_event_df = ae_event_df.loc[ae_event_df["variable"].str.contains("Niveau"),:]
        ae_event_df = ae_event_df.loc[mask,:]
    # add +- 2d to start and end
    ae_event_df["start"] = ae_event_df["start"] - pd.Timedelta(days=2)
    ae_event_df["end"] = ae_event_df["end"] + pd.Timedelta(days=2)
    # add Y_M column
    ae_event_df["Y_M"] = ae_event_df["start"].dt.strftime("%Y_%m")
    # create string for mutliselect
    ae_event_df["multi"] = ""
    for i in ae_event_df.index.to_list():
        ae_event_df.loc[i,"multi"] = f"{ae_event_df.loc[i,'length']} Min - {ae_event_df.loc[i,'variable']} - {ae_event_df.loc[i,'Y_M']}"
    return ae_event_df
