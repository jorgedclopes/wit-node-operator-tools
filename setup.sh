#!/bin/bash

pip3 install -r requirements.txt
pip3 install -e .

python3 setup_server/setup_server.py --overwrite-servers

rm -rf ~/.grafana
cp -rf grafana ~/.grafana

rm -rf ~/.prometheus
cp -rf prometheus ~/.prometheus

docker-compose up -d
