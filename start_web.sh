#!/bin/bash

# Default port if none is provided
PORT=${1:-5000}

# Get the absolute path to the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the FLASK_APP environment variable to the absolute path of the app
export FLASK_APP="$SCRIPT_DIR/src/shiver/web/app.py"

# Run the flask app
echo "Starting Shiver web application..."
echo "Access it at http://127.0.0.1:$PORT"
echo "Press Ctrl+C to stop the server."
python3 -m flask run --port=$PORT
