#!/usr/bin/env bash

# This script creates self signed certificates for all the services

SERVICE=teleshake
PATH_STEM=$SERVICE/$SERVICE

# Private key
openssl genrsa -out $PATH_STEM.key 2048

# Certificate signing request
openssl req -key $PATH_STEM.key -new -out $PATH_STEM.csr

# Self signed certificate
openssl x509 -signkey $PATH_STEM.key -in $PATH_STEM.csr -req -days 365 -out $PATH_STEM.pem