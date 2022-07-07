terraform {
    required_providers {
        google = {
            source  = "hashicorp/google"
            version = "3.5.0"
        }
    }
}

###################################################################################################
# Google
###################################################################################################

provider "google" {
    credentials = file("credentials/google-cloud-adpipe-d56647c97fd7.json")

    region = var.GOOGLE_CLOUD_PROJECT_REGION
    project = var.GOOGLE_CLOUD_PROJECT_NAME
}


#################################################
# Google Environment Variables
#################################################

variable "GOOGLE_CLOUD_SQL_PASSWORD" {
    type = string
    description = "Password to initialize the MySQL instance's root user with."
    sensitive = true
}

variable "GOOGLE_CLOUD_PROJECT_NAME" {
  type = string
  description = "Name of the Google Cloud project for initializing Google Cloud resources."
}

variable "GOOGLE_CLOUD_PROJECT_REGION" {
    type = string
    description = "Google Cloud region to use for the resources."
}

variable "GOOGLE_CLOUD_INSTANCE_NAME" {
    type = string
    description = "Name of the Google Cloud SQL instance."
}

variable "GOOGLE_CLOUD_BUCKET_NAME" {
    type = string
    description = "Name of the Google Cloud Storage bucket."
}

variable "GOOGLE_APPLICATION_CREDENTIALS" {
    type = string
    description = "Path to Google Cloud's service account credentials JSON."
    sensitive = true
}

#################################################
# Google Resources
#################################################

resource "google_sql_database_instance" "main" {
    name             = var.GOOGLE_CLOUD_INSTANCE_NAME
    database_version = "MYSQL_8_0"

    settings {
        tier              = "db-f1-micro"
        pricing_plan      = "PER_USE"
        activation_policy = "ALWAYS"
        availability_type = "ZONAL"

        # Storage
        disk_autoresize        = false
        disk_size              = 10
        disk_type              = "PD_HDD"

        backup_configuration {
            binary_log_enabled = false
            enabled            = false
            start_time = "19:00"
        }

        ip_configuration {
            ipv4_enabled = true
            require_ssl  = false
        }

    }

    timeouts {
        create = null
        delete = null
        update = null
    }

}

resource "google_sql_user" "users" {
    name = "root"
    instance = google_sql_database_instance.main.name
    password = var.GOOGLE_CLOUD_SQL_PASSWORD
}

resource "google_storage_bucket" "bucket" {
    name = var.GOOGLE_CLOUD_BUCKET_NAME
    
}