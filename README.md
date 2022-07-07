# AdPipe

<div>
    <img src="https://img.shields.io/static/v1?label=Latest&message=v0.0.1-Beta&color=informational">
    <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=important">
    <img src="https://img.shields.io/static/v1?label=MySQL&message=8.0&color=important">
</div>

Cloud pipeline for artificial user advertising data from the [Context Ad Clicks Dataset](https://www.kaggle.com/datasets/arashnic/ctrtest).

## Index

- [Setting Up](#setting-up)
    - [Environment Variables](#environment-variables)
    - [Terraform Environment](#terraform-environment-variables)
- [Loading](#loading)

<div id="setting-up"></div>

## Setting Up

### Clone this repository

`git clone https://github.com/dominictarro/AdPipe.git`

### Infrastructure

#### **Terraform**

You can configure your infrastructure via Terraform by following.

1. Create a project, set up permissions, and enable the APIs as shown in [Getting Started with Terraform](https://cloud.google.com/docs/terraform/get-started-with-terraform).
1. Set the [Terraform .env variables](#terraform-env).
1. Once those are complete,

```bash
scripts/terraform.sh
```

#### **Google Cloud Platform**

If you do not want to use Terraform, follow these instructions.

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

<div id="#environment-variables"></div>

### Environment Variables

In a `.env` file, include the following variables

```conf
# Example
GOOGLE_CLOUD_SQL_PASSWORD=a_secURe_pa55word
GOOGLE_CLOUD_INSTANCE_NAME=main                                 # Required for loading scripts

GOOGLE_CLOUD_PROJECT_NAME=adpipe                                # Required for loading scripts
GOOGLE_CLOUD_PROJECT_REGION=us-east-1                           # Required for loading scripts

GOOGLE_CLOUD_BUCKET_NAME=adpipe

GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloud-credentials.json  # Required for Google Cloud Python API

```

<div id="#terraform-environment-variables"></div>

#### Terraform Environment Variables

These should be approximately the same as the above environment variables, but all have the preamble `TF_VAR`.

! **You still need to include the above variables in the `.env`**

The only variable that might be different from the above is the project region. Google Cloud's REST API accepts a different region label than the service integration with Terraform.

```sh
# Example
TF_VAR_GOOGLE_CLOUD_SQL_PASSWORD=a_secURe_pa55word
TF_VAR_GOOGLE_CLOUD_INSTANCE_NAME=main

TF_VAR_GOOGLE_CLOUD_PROJECT_NAME=adpipe
# notably different from the region label used by the loading scripts
TF_VAR_GOOGLE_CLOUD_PROJECT_REGION=us-east1

TF_VAR_GOOGLE_CLOUD_BUCKET_NAME=adpipe

TF_VAR_GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloud-credentials.json
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
