import os
import subprocess
from pathlib import Path

## Development server requires we first copy all common libraries
if __name__ == "__main__":
    # subprocess.check_output('cp -nr ../../common/ .')
    f_path = Path(__file__)
    #source = os.path.join(f_path.parent.parent.parent, 'common/')
    #dest = str(f_path.parent) + '/'

    #output =subprocess.check_output(['rsync', '-a', '-v', source, dest])


from utils.constants import constants


from ast import For
from flask import Flask, app, render_template, request, flash, jsonify
# from numpy.lib.function_base import append
import pandas as pd
import numpy as np

import uuid

from pprint import pprint
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive Agg backend
from matplotlib import pyplot as plt
import scipy.stats as stats
from werkzeug.utils import secure_filename
from benefit_diagram import compute_benefits
from dominance_diagram import compute_chi_diagrams
from paired_plot import paired_plot
import metrics
import conversion_script
from metrics import compute_effects
#from reliance_pattern_diagram import trust_diagram
from create_reliances import create_reliances, process_csv_files
from create_reliances_new import create_reliances, convert_csv
# work in progress
from sankey import sankey
from stacked import stacked
from single_paired import single_paired
import io
import logging

# Creiamo un file di log personalizzato
# Old Linux-style path (problematic on Windows):
# logging.basicConfig(filename='/home/HAIIAssessment/mysite/error.log', level=logging.DEBUG)

# New Windows-compatible version:
# log_dir = os.path.join("HAIIAssessment", "mysite")
# os.makedirs(log_dir, exist_ok=True)  # Creates directory if needed
# log_file = os.path.join(log_dir, "error.log")
# logging.basicConfig(filename=log_file, level=logging.DEBUG)

# Aggiungiamo una riga per confermare che il logging funziona
# logging.debug("App Flask avviata")
# end of WIP

def create_app():
    app_name = 'haiiassessment'
    print(f'App Name = {app_name}')

    # Creazione dell'app Flask
    app = Flask(__name__, instance_relative_config=True)
    @app.context_processor
    def inject_constants():
        return dict(constants=constants)
    filepath = __file__.rsplit('/', 1)
    path = filepath[0]
    # path = os.getcwd()

    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    ALLOWED_FILES = {'csv'}
    TEST_FOLDER = os.path.join(path, 'testfiles/')

    # app = Flask(__name__)
    # print("app")

    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.mkdir(UPLOAD_FOLDER)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["ALLOWED_FILES"] = ALLOWED_FILES
    app.config["SECRET_KEY"] = 'f13783376341d2dddfaef175'
    app.config['TEST_FOLDER'] = TEST_FOLDER

    @app.context_processor
    def inject_constants():
        return dict(constants=constants)

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_FILES


    @app.route("/qr", methods=['POST', 'GET'])
    @app.route("/rp", methods=['POST', 'GET'])
    @app.route("/", methods=['POST', 'GET'])
    def choose_form(test=False):
        # Windows-compatible alternative to running clean.sh
        if os.path.exists("clean.bat"):
        #     subprocess.Popen(["clean.bat"], shell=True)
        # elif os.path.exists("clean.sh"):
        #     # For Windows Subsystem for Linux (WSL) users
        #     subprocess.Popen(["wsl", "./clean.sh"])
            try:
                # Make sure the script has execute permissions
                os.chmod("clean.sh", 0o755)
                # Run directly (no WSL needed in Docker)
                subprocess.Popen(["/bin/bash", "./clean.sh"])
            except Exception as e:
                logging.error(f"Clean script failed: {e}")

        # for key, value in request.form.items():
        #     print(f"{key}: {value}")

        # Results page
        if request.method == 'POST':

            if request.form.get('submit', False) == 'submit_dataset':

                input_data = request.files['reliance']
                #sep = ','

                if input_data.filename == '':
                    flash("Input file is necessary", category='warning')
                    return render_template('upload.html')

                if not allowed_file(input_data.filename):
                    flash("Input file needs .csv extension", category='danger')
                    return render_template('upload.html')
                # WORK IN PROGRESS
                current_file = input_data
                file_content = io.StringIO(current_file.stream.read().decode('utf-8'))
                sample = file_content.read(100)
                file_content.seek(0)
                delimiter = ';' if ';' in sample and ',' not in sample else ','
                if delimiter == ';':
                    corrected_content = file_content.getvalue().replace(';', ',')
                    # corrected_file = io.StringIO(corrected_content)

                    current_file.stream = io.BytesIO(corrected_content.encode('utf-8'))
                    current_file.stream.seek(0)
                else:
                    corrected_content = file_content.getvalue()
                    current_file.stream = io.BytesIO(corrected_content.encode('utf-8'))
                    current_file.stream.seek(0)
                #END OF WIP

                #first_line = input_data.readline()
                #if ';' in first_line and ',' not in first_line:
                #    sep = ';'
                #else:
                #    sep = ','
            if request.form.get('submit', False) == 'submit_questionnaire':
                uuiddir = str(uuid.uuid4())
                dataset = request.files['qr1']
                ai_response = request.files['qr2']
                groundtruth = request.files['qr3']

                if dataset.filename == '' or ai_response.filename == '' or groundtruth.filename == '':
                    flash("Input files are necessary", category='warning')
                    return render_template('upload.html')
                if not allowed_file(dataset.filename) or not allowed_file(ai_response.filename) or not allowed_file(groundtruth.filename):
                    flash("Input files needs .csv extension", category='danger')
                    return render_template('upload.html')

                # quest_path_dir = "./uploads/" + uuiddir
                quest_path_dir = os.path.join(path, "uploads", uuiddir)

                os.mkdir(quest_path_dir)

                # WORK IN PROGRESS
                for current_file in [dataset, ai_response, groundtruth]:
                    file_content = io.StringIO(current_file.stream.read().decode('utf-8'))
                    sample = file_content.read(100)
                    file_content.seek(0)
                    delimiter = ';' if ';' in sample and ',' not in sample else ','
                    if delimiter == ';':
                        corrected_content = file_content.getvalue().replace(';', ',')
                        # corrected_file = io.StringIO(corrected_content)

                        current_file.stream = io.BytesIO(corrected_content.encode('utf-8'))
                        current_file.stream.seek(0)
                    else:
                        corrected_content = file_content.getvalue()
                        current_file.stream = io.BytesIO(corrected_content.encode('utf-8'))
                        current_file.stream.seek(0)

                # END OF WIP

                dataset_path = os.path.join(quest_path_dir, "base_dataset.csv")
                ai_response_path = os.path.join(quest_path_dir, "base_ai.csv")
                groundtruth_path = os.path.join(quest_path_dir, "base_gt.csv")

                # Salvataggio dei file
                dataset.save(dataset_path)
                ai_response.save(ai_response_path)
                groundtruth.save(groundtruth_path)

                # Lettura dei file con Pandas
                dataset = pd.read_csv(dataset_path, sep=',')
                ai_response = pd.read_csv(ai_response_path, sep=',')
                groundtruth = pd.read_csv(groundtruth_path, sep=',')

                # Rimozione di eventuali spazi nei nomi delle colonne
                dataset.columns = dataset.columns.str.strip()
                ai_response.columns = ai_response.columns.str.strip()
                groundtruth.columns = groundtruth.columns.str.strip()

                    # Elaborazione dei file
                try:
                    process_csv_files(quest_path_dir, "base_dataset.csv")
                except ValueError as e:
                    flash(str(e), category='danger')
                    return render_template('upload.html')
                except Exception as e:
                    flash("Errore imprevisto: " + str(e), category='danger')
                    return render_template('upload.html')


                # Percorso dell'output generato dallo script
                input_data = os.path.join(quest_path_dir, "base_dataset_reliances.csv")

            try:
                data = pd.read_csv(input_data, sep=',').squeeze("columns")
                required_columns = ['HD1', 'AI', 'FHD']
                data = data.dropna(how='all')
                data = data.dropna(how='any')

                for col in required_columns:
                    if col not in data.columns:
                        flash(f"Mandatory field {col} is missing", category='danger')
                        return render_template('upload.html')

                missing_values = data.isna().sum().sum()
                if (missing_values > 0):
                    flash("The uplodaded file has one or more missing values.", category='danger')
                    return render_template('upload.html')
                if "Type_AI" not in data.columns:
                    data["Type_AI"] = "Support"
                if "Study" not in data.columns:
                    data["Study"] = ""
                if "Complexity" not in data.columns:
                    data["Complexity"] = ""
                if "Type_H" not in data.columns:
                    data["Type_H"] = ""
                if "id" not in data.columns:
                    data["id"] = ""

            except Exception as e:
                print(f"Error detected: {e}")
                flash("Unable to read input data, incorrect format in CSV files. Please check and try again.", category='danger')
                return render_template('upload.html')

            return render(data)

        if test is True:

            # data = pd.read_csv("./static/testfiles/sample_data.csv", sep=',').squeeze("columns")
            test_data_path = os.path.join(path, "static/testfiles/sample_data.csv")
            data = pd.read_csv(test_data_path, sep=',').squeeze("columns")

            # return render(data, magnitude)
            return render(data)

        return render_template('home.html')

    def render(data):
        try:
            print("Avvio compute_benefits()...")
            benefit_diagrams = list(compute_benefits(data))
            print("compute_benefits() completato.")


            print("Avvio compute_chi_diagrams()...")
            filenames2 = list(compute_chi_diagrams(data, True))
            print("compute_chi_diagrams(True) completato.")

            print("Avvio compute_chi_diagrams() senza cut...")
            nocut_filenames2 = list(compute_chi_diagrams(data, False))
            print("compute_chi_diagrams(False) completato.")

            reliance_files = [f for f in filenames2 if "reliance_" in f]

            # WORK IN PROGRESS
            # reliance_patterns = list(zip(reliance_files,["Pattern " + str(i+1) for i in range(len(reliance_files))]))
            study_names = ["Study"]
            if len(list(data["Study"].unique())) > 1:
                study_names = list(data["Study"].unique())
            reliance_patterns = list(zip(reliance_files, study_names))
            # end of WIP

            print("dominance diagrams", filenames2[0], nocut_filenames2[0])

            dominance_diagrams = [filenames2[0], nocut_filenames2[0]]

            # Gestione dei grafici per l'Automation Bias (Frequency)
            cog_impact_diagrams = []
            automation, conservatism, automation_nocut, conservatism_nocut = "","","",""
            for filename in [filenames2[1], filenames2[2]]:
                if filename and "Automation Bias" in filename and not "Causal" in filename:
                    automation = filename
                elif filename and "Conservatism Bias" in filename and not "Causal" in filename:
                    conservatism = filename

            for filename in [nocut_filenames2[1], nocut_filenames2[2]]:
                if filename and "Automation Bias" in filename and not "Causal" in filename:
                    automation_nocut = filename
                elif filename and "Conservatism Bias" in filename and not "Causal" in filename:
                    conservatism_nocut = filename

            cog_impact_diagrams.append(automation);
            cog_impact_diagrams.append(automation_nocut);
            cog_impact_diagrams.append(conservatism);
            cog_impact_diagrams.append(conservatism_nocut);

            # Gestione dei grafici per l'Automation Bias (Causal)
            causal_diagrams = []
            for filename in [filenames2[1], nocut_filenames2[1], filenames2[2], nocut_filenames2[2],filenames2[3], nocut_filenames2[3], filenames2[4], nocut_filenames2[4]]:
                if filename and ("Automation Bias (Causal)" in filename or "Conservatism Bias (Causal)" in filename):
                    causal_diagrams.append(filename)

            # Gestione fallback in caso di grafici mancanti
            if len(causal_diagrams) < 2:
                causal_diagrams.extend([None] * (2 - len(causal_diagrams)))


            print("Avvio paired_plot()...")
            paired_p = list(paired_plot(data))
            print("paired_plot() completato.")

            if not paired_p:
                raise ValueError("Nessun paired plot generato")

            print("Avvio compute_effects()...")
            metrics_data = compute_effects(data)
            print("compute_effects() completato.")
            sankey_diagram = sankey(data) # OK
            # stacked_plot = stacked(data) #OK
            single_paired_plot = list(single_paired(data)) #OK

            rounded_metrics=[]


            for metrics in metrics_data :
                rounded_metrics_data = {}
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        rounded_metrics_data[key] = round(value, 3)
                    else:
                        rounded_metrics_data[key] = value
                rounded_metrics.append(rounded_metrics_data)

            return render_template('results.html', benefit_diagrams=benefit_diagrams, dominance_diagrams=dominance_diagrams, cog_impact_diagrams=cog_impact_diagrams, reliance_patterns=reliance_patterns, causal_diagrams=causal_diagrams, paired_plot=paired_p, metrics_data=rounded_metrics, single_paired_plot=single_paired_plot, sankey_diagram=sankey_diagram)
        except Exception as e:
            print(f'error detected {e}')
            flash("Unable to read input data, incorrect data format in csv files, please check the data and try again", category='danger')

    @app.route('/test')
    def test():
        try:
            return choose_form(test=True)
        finally:
            # Ensure cleanup happens even if there's an error
            plt.close('all')
            import gc
            gc.collect()  # Force garbage collection
        
    @app.route('/upload')
    def upload():
        return render_template('upload.html')

    @app.route('/reliancePattern')
    def reliancePattern():
        return render_template('./inputs/reliancePattern.html')

    @app.route('/questionnaireResponses')
    def questionnaireResponses():
        return render_template('./inputs/questionnaireResponses.html')

    @app.route("/deploy")
    def deploy():
        output = subprocess.check_output('./lib/deploy.sh', stderr=subprocess.STDOUT).replace(b'\n', b'<br />')

        return output


    if __name__ == '__main__':
        app.run(debug=True)
    
    # return app
    return app
