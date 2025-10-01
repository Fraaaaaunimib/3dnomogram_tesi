FROM python:3.13-slim

WORKDIR /app

# 1. First copy only requirements.txt to cache pip installs
COPY requirements.txt .

# 2. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install scikit-learn plotly kaleido

# 3. Copy all remaining files
COPY . .

# 4. Prepare clean.sh and directories
RUN chmod +x clean.sh && \
    apt-get update && apt-get install -y dos2unix && \
    dos2unix clean.sh && \
    mkdir -p HAIIAssessment/mysite && \
    mkdir -p HAIIAssessment/static/output1 && \
    mkdir -p HAIIAssessment/static/output2 && \
    mkdir -p HAIIAssessment/static/output3 && \
    mkdir -p HAIIAssessment/static/output4 && \
    mkdir -p HAIIAssessment/templates/user-generated && \
    mkdir -p HAIIAssessment/uploads && \
    mkdir -p uploads && \
    apt-get remove -y dos2unix && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Environment variables
ENV FLASK_APP=flask_app_windows.py
ENV FLASK_ENV=development
ENV UPLOAD_FOLDER=/app/uploads

EXPOSE 5001
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]