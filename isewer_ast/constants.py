import sys
### STATIC VARIABLES

#INITIAL_VOI = "Niveau_RÜ_BerlinerAllee"
INITIAL_VOI = "FSR_Rückwärts_RÜ_Hindenburgstraße"
# Inital Columns"
INITIAL_COLS0 = ["Niveau_RÜ_BerlinerAllee"] + [INITIAL_VOI]
INITIAL_COLS1 = []#"FSR_Rückwärts_RÜ_Hindenburgstraße"

Z_THRESHOLD = 20# Zscore threshold
N_AE_ANOMALIES = 200#top n in anomaly length
FILTER_ANOMALIES = False# filter for niveau, not at NORD or SK

# different to encoding from labelling (nan, 0, 1), here nan, 0.1:sensor anomaly, 0.2:system anomaly, 0.3:other
# classifications only hold na/0/1 but are recoded upon load
# Check Label-Plot ylimits if including 0.1-0.3
LABELS = ["Sensor Anomaly", "System Anomaly", "Other", "AE Anomaly"]
LABELCOLORS = ["lightblue", "darkred","gray", "darkgreen"]

### Choice of Variables to plot
MULTI_LIST_WIDTH = 220
MULTI_LIST_WIDTH2 = 300

### Plotting parameters
### CREATE PLOTS
TOOLS0 = "pan,box_zoom,ywheel_zoom,box_select,reset"#
TOOLS1 = "pan,box_zoom,ywheel_zoom,reset"#
WIDTH, HEIGHT = 1500,350
HEIGHT1 = 100


### FILEPATHS
if "ftp" in sys.argv:
    DATADIR = "/data/isewer/data/011_split_by_year_month_ftp/by_month/"
    DATADIR_CL = "/data/isewer/data/classifications_ftp/by_year_month/by_month/"
    PATH_AE_ANOMALIES = f"/home/schmidle/code/isewer/anomaly_detection/results/010_process_daily_files/ae_event_df_zthresh{Z_THRESHOLD}_ftp.feather"
    PATH_AE_ANOMALIES_MANUAL = f"/home/schmidle/code/isewer/anomaly_detection/results/003_AE_classifications/manual_labels_event_df.feather"
    INITIAL_FILE = "2023_12"
    print("-------------------FTP DATA-------------------")
else:    
    DATADIR = "/data/isewer/data/011_split_by_year_month/by_month/"
    DATADIR_CL = "/data/isewer/data/classifications/by_year_month/by_month/"
    PATH_AE_ANOMALIES = f"/home/schmidle/code/isewer/anomaly_detection/results/003_AE_classifications/ae_event_df_zthresh{Z_THRESHOLD}.feather"
    INITIAL_FILE = "2021_06"
    print("-------------------TESTTRAIN DATA-------------------")
