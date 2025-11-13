#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pip install -r src/backend/requirements.txt

python src/backend/manage.py upgrade
