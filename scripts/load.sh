#!/bin/bash
# Script for loading the data into a Google Cloud SQL database.
# 
# 1. Downloads data from https://www.kaggle.com/datasets/arashnic/ctrtest/download
# 2. Downloads data for fake data generation
# 3. Generates fake data to populate tables
# 4. Loads data into database

function download_kaggle() {
    if ! [ -d kaggle_raw ]; then
        mkdir kaggle_raw
    fi
    cd kaggle_raw

    echo Downloading Kaggle data
    kaggle datasets download 'arashnic/ctrtest' --wp --unzip
    
    # return to data
    cd ..
}

function download_generator_inputs() {
    if ! [ -d generator_input ]; then
        mkdir generator_input
    fi
    cd generator_input

    download_country_codes
    #download_country_timezones

    # return to data
    cd ..
}

function download_country_codes() {
    echo Downloading country code data
    wget 'https://raw.githubusercontent.com/datasets/country-codes/master/data/country-codes.csv' --tries=3 --show-progress
    if [ -f country-codes.csv.1 ]; then
        mv country-codes.csv.1 country-codes.csv
    fi
}

function download_country_timezones() {
    echo Downloading country timezone data
    wget 'https://raw.githubusercontent.com/manuelmhtr/countries-and-timezones/master/src/data.json' --tries=3 --show-progress --output-document=country-timezones.json
    if [ -f country-timezones.json.1 ]; then
        mv country-timezones.json.1 country-timezones.json
    fi
}


function download_data() {
    # Assumes script call from project home directory
    if ! [ -d data ]; then
        mkdir data
    fi
    cd data

    download_kaggle
    download_generator_inputs
    
    cd ..
}

download_data
if [ $? -eq 0 ]; then
    echo Building tables \
    && python scripts/build_tables.py \
    && echo Initializing Google Cloud database \
    && python scripts/initialize_cloud_tables.py \
    && echo Uploading table data to Google Cloud \
    && python scripts/upload_tables_to_cloud_storage.py \
    && echo Importing data to Google Cloud database \
    && python scripts/import_tables_from_bucket.py

    if [ $? -eq 0 ]; then
        echo 'Purging local copy of table data'
        #rm -r data/*
    fi
fi
