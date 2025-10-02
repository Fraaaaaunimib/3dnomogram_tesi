#! /bin/bash

set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate
export PYTHONPATH="$PWD" 


echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install scikit-learn plotly kaleido

echo "Setting Flask environment variables..."

export FLASK_APP=flask_app_mac.py
export FLASK_ENV=development

echo "Creating project directories locally..."
mkdir -p static/output1 static/output2 static/output3 static/output4 templates/user-generated uploads

if [ -f "clean_mac.sh" ]; then
    chmod +x clean_mac.sh
fi

echo "Starting Flask application..."
flask run --host=0.0.0.0 --port=5001