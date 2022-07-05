# AdPipe

<img src="https://img.shields.io/static/v1?label=Latest&message=v0.0.1-Beta&color=informational">
<img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=important">
<img src="https://img.shields.io/static/v1?label=MySQL&message=8.0&color=important">

Cloud pipeline for artificial user advertising data from the [Context Ad Clicks Dataset](https://www.kaggle.com/datasets/arashnic/ctrtest).

## Index

- [Setting Up](#setting-up)
- [Loading](#loading)

<div id="setting-up"></div>

## Setting Up

### Clone this repository

`git clone https://github.com/dominictarro/AdPipe.git`

### Google Cloud Basics

1. [Create a Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
1. [Create a MySQL instance & database with Google Cloud](https://cloud.google.com/sql/docs/mysql/create-manage-databases)
    - This project requires no more than 10 GB of MySQL storage
    - Database should be named '*production*'
1. [Create an IAM service account and download the JSON credentials](https://cloud.google.com/docs/authentication/getting-started)
1. [Enable the Cloud SQL Admin API](https://cloud.google.com/sql/docs/mysql/admin-api#gcloud)

### Python

Create a virtual environment

```bash
# Install pipenv to system python
pip install pipenv

# Create a virtual environment and install packages to it
cd /path/to/project && \
python3.9 -m venv venv && \
source venv/bin/activate && \
pipenv install
```

### Environment Variables

In a `.env` file, include the following variables

```conf
# Example
GOOGLE_CLOUD_PROJECT_NAME=adpipe                                # Required for loading scripts
GOOGLE_CLOUD_PROJECT_REGION=us-east-1                           # Required for loading scripts
GOOGLE_CLOUD_INSTANCE_NAME=main                                 # Required for loading scripts
GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloud-credentials.json  # Required for Google Cloud Python API
```

<div id="loading"></div>

## Loading the artificial data

After your Cloud project and environment is set, run the following in the virtual environment

```bash
scripts/load.sh
```

This will

1. Download
    - Kaggle data
    - Generator data
1. Generate artificial data
1. Format tables
1. Upload table CSVs to Google Cloud Storage
1. Import to the production database
