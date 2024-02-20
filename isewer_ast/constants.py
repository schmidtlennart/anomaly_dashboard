### STATIC VARIABLES

### LAYOUT/DATA
INITIAL_FILE = "2021_06"
#INITIAL_VOI = "Niveau_RÜ_BerlinerAllee"
INITIAL_VOI = "FSR_Rückwärts_RÜ_Hindenburgstraße
# Inital Columns"
INITIAL_COLS0 = ["Niveau_RÜ_BerlinerAllee","Niveau_RÜ_Uferstraße"]
INITIAL_COLS1 = ["FSR_Rückwärts_RÜ_Hindenburgstraße"]

# different to encoding from labelling (nan, 0, 1), here nan, 0.1:sensor anomaly, 0.2:system anomaly, 0.3:other
# classifications only hold na/0/1 but are recoded upon load
# Check Label-Plot ylimits if including 0.1-0.3
LABELS = ["Sensor Anomaly", "System Anomaly", "Other", "AE Anomaly"]
LABELCOLORS = ["lightblue", "darkred","gray", "darkgreen"]

### Choice of Variables to plot
MULTI_LIST_WIDTH = 220

### Plotting parameters
### CREATE PLOTS
TOOLS0 = "pan,box_zoom,ywheel_zoom,box_select,reset"#
TOOLS1 = "pan,box_zoom,ywheel_zoom,reset"#
WIDTH, HEIGHT = 1500,350
HEIGHT1 = 100


### FILEPATHS
DATADIR = "/data/isewer/data/011_split_by_year_month/by_month/"
DATADIR_CL = "/data/isewer/data/classifications/by_year_month/by_month/"
