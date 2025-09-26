#!/bin/bash

MARKER_FILE=".setup_done"

if [ ! -f "$MARKER_FILE" ]; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "requirements.txt not found."
        exit 1
    fi
    touch "$MARKER_FILE"
    echo "Setup completed and marker file created."
else
    echo "Setup already completed. Marker file exists."
fi

#Run the python code
python src/scenario_analyzer.py #Runs forever

exit 0