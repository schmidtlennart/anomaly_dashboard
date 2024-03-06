#!/bin/bash

source /home/schmidle/VirtualEnvs/anomaly_selection_tool/bin/activate
# get path depending on arg passed in and start bokeh server
if [ $1 = "ast" ]; then
    path="/home/schmidle/code/anomaly_selection_tool/dashboards/isewer_ast.py"
    args=""
fi
if [ $1 = "class" ]; then
    path="/home/schmidle/code/anomaly_selection_tool/isewer_classifications.py"
    args=""
fi
if [ $1 = "ftp_class" ]; then
    path="/home/schmidle/code/anomaly_selection_tool/isewer_classifications.py"
    args="ftp"
fi
bokeh serve --dev --port 8992 --allow-websocket-origin=localhost:9999 $path --args $args
