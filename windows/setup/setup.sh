#!/bin/sh
echo "Installing all dependencies"
pip install -r requirements.txt
echo "Init Postgres DB"
python db.py