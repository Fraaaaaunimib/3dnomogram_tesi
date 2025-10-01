@echo off

REM --- 1. Create and activate a Python virtual environment ---
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate

REM --- 2. Install Python dependencies ---
echo Installing Python dependencies...
pip install -r requirements.txt
pip install scikit-learn plotly kaleido

REM --- 3. Set Flask environment variables ---
echo Setting Flask environment variables...
set FLASK_APP=flask_app_windows.py
set FLASK_ENV=development

REM --- 4. Create project directories ---
echo Creating project directories...
md HAIIAssessment\mysite 2>nul
md HAIIAssessment\static\output1 2>nul
md HAIIAssessment\static\output2 2>nul
md HAIIAssessment\static\output3 2>nul
md HAIIAssessment\static\output4 2>nul
md HAIIAssessment\templates\user-generated 2>nul
md HAIIAssessment\uploads 2>nul

IF EXIST flask_app_windows.py (
    echo Starting Flask application...
    flask run
) ELSE (
    echo Error: flask_app_windows.py not found!
)