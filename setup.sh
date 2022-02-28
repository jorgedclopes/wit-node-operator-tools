#!/bin/bash

#apt install python3-pip
pip3 install -r requirements.txt
pip3 install -e .

python3 setup_server/setup_server.py --overwrite-servers

rm -rf ~/.prometheus
cp -rf prometheus ~/.prometheus

rm -rf ~/.grafana
cp -rf grafana ~/.grafana

docker-compose up -d
