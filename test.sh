#!/bin/bash

source .env.test
sudo -u ${DATABASE_USER} psql -c "CREATE DATABASE ${DATABASE_NAME};"

./test-setup.sh
./test-unit.sh
./test-integration.sh
