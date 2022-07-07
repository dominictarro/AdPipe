#!/bin/bash

# export environment variables
set -o allexport
source .env
set +o allexport

terraform apply