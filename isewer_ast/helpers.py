import os

def get_filenames(dir):
    # Create dict of input file paths
    FILES = {}
    for file in sorted(os.listdir(dir)):
        if ("2022_" in file) | ("2021_" in file):#filter for 2021+2022
            FILES[file[:7]] = dir+file
    return FILES

def columns_to_pr_label(cols):
    # turn columns into labels, predictions and their labels
    pr = ["pr_"+c for c in cols]
    label = ["pr_"+c+"_Label" for c in cols]
    return cols+pr+label