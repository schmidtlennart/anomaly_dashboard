#!/bin/bash

source /home/schmidle/VirtualEnvs/anomaly_selection_tool/bin/activate
# get path depending on arg passed in and start bokeh server
if [ $1 = "ast" ]; then
    path="/home/schmidle/code/anomaly_selection_tool/dashboards/isewer_ast.py"
fi
if [ $1 = "preds" ]; then
    path="/home/schmidle/code/anomaly_selection_tool/dashboards/isewer_predictions.py"
fi
bokeh serve --dev --port 8992 --allow-websocket-origin=localhost:9999 $path
