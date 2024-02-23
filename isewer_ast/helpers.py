import os
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource


def get_filenames(dir):
    # Create dict of input file paths
    FILES = {}
    for file in sorted(os.listdir(dir)):
        if ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
            FILES[file[:7]] = dir+file
    return FILES

def columns_to_pr_label(cols):
    # if list of lists, flatten
    if isinstance(cols[0], list):
        cols = [item for sublist in cols for item in sublist]
   # turn columns into labels, predictions and their labels
    pr = ["pr_"+c for c in cols]
    label = ["pr_"+c+"_Label" for c in cols]
    return cols+pr+label

def create_data_source(FILES, FILES_PR, file, current_cols):
    # observed
    data = pd.read_feather(FILES[file])#columns=read_cols
    print("data loaded") 
    data.DateTime = pd.to_datetime(data.DateTime)# no need to set format because done in "011_load_to_feather.py"
    # predictions
    data_pr = pd.read_feather(FILES_PR[file])#columns=read_cols
    print("data_pr loaded") 
    # reduce both to the inner join set of columns, i.e. also remove labels
    cols_joint_label = list(set(data.columns.to_list())& set(data_pr.columns.to_list()))
    # drop all with _Label
    cols_joint = [c for c in cols_joint_label if not c.endswith("_Label")]
    data = data.loc[:,cols_joint]
    # add labels back in for predictions
    data_pr = data_pr.loc[:,cols_joint+cols_joint_label]
    # rename to make clear that its predicions
    data_pr.columns = ["pr_"+c for c in data_pr.columns]
    # recode labels 0 to np.nan forplotting
    data_pr_plot = data_pr.copy()
    data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")] = data_pr_plot.loc[:,data_pr_plot.columns.str.contains("_Label")].replace({0:np.nan})

    ### merge predictions and observed data
    alldata = pd.concat([data,data_pr_plot], axis=1)

    load_cols = ["DateTime"] + columns_to_pr_label(current_cols)
    source = ColumnDataSource(alldata.loc[:,load_cols])
    print("(re-)created datasource")
    # return data source, alldata (i.e. data, pr_data and pr_labels) and all data columns (for col selection so withour _pr or _Label)
    return source, alldata, data.columns.to_list()