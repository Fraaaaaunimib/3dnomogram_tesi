#!/bin/bash

# 1. Create a Python virtual environment (if not exists)
python -m venv venv
source venv/Scripts/activate  # Activate venv (Git Bash on Windows)

# 2. Install Python dependencies
pip install -r requirements.txt
pip install scikit-learn plotly kaleido

# 3. Set Flask environment variables
export FLASK_APP=flask_app_windows.py
export FLASK_ENV=development

# 4. Create project directories (Windows-compatible paths)
mkdir -p HAIIAssessment/mysite
mkdir -p HAIIAssessment/static/{output1,output2,output3,output4}
mkdir -p HAIIAssessment/templates/user-generated
mkdir -p HAIIAssessment/uploads

# 5. Make clean.sh executable (if it exists)
if [ -f "clean.sh" ]; then
    chmod +x clean.sh
fi

# 6. Run Flask (if flask_app.py exists)
if [ -f "flask_app_windows.py" ]; then
    flask run
else
    echo "Error: flask_app_windows.py not found!"
fi