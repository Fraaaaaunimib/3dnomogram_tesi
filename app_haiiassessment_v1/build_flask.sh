#! /bin/bash

sudo dnf install python3-pip
pip3 install -r requirements.txt

pip install scikit-learn
pip install plotly
pip install kaleido

export FLASK_APP=flask_app.py

export FLASK_ENV=development

chmod +x clean.sh

cd /home
mkdir HAIIAssessment
sudo chown fedora:fedora HAIIAssessment/
cd HAIIAssessment
mkdir mysite
mkdir static
mkdir templates
mkdir uploads
cd static
mkdir output1
mkdir output2
mkdir output3
mkdir output4
cd ..
cd templates
mkdir user-generated

flask run
