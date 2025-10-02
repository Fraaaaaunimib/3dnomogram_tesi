@echo off

echo Activating virtual environment...
IF NOT EXIST venv (
	echo Creating virtual environment...
	python -m venv venv
)
call venv\Scripts\activate
set "PYTHONPATH=%cd%"


echo Setting Flask environment variables...
set FLASK_APP=flask_app_windows.py
set FLASK_ENV=development

REM --- 4. Create project directories ---
echo Creating project directories...
md mysite 2>nul
md static\output1 2>nul
md static\output2 2>nul
md static\output3 2>nul
md static\output4 2>nul
md templates\user-generated 2>nul
md uploads 2>nul

IF EXIST flask_app_windows.py (
    echo Starting Flask application...
    flask run
) ELSE (
    echo Error: flask_app_windows.py not found!
)