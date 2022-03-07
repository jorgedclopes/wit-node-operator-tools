#!/bin/bash

apt update
if [ $(which pip3 | wc -l) ]
then
  apt install python3-pip -y
fi

pip3 install -r requirements.txt
pip3 install -e .

python3 setup_server/setup_server.py --overwrite-servers

rm -rf ~/.prometheus
cp -rf prometheus ~/.prometheus

rm -rf ~/.grafana
cp -rf grafana ~/.grafana
rm ~/.grafana/provisioning/datasources/.datasource.yml

docker-compose up -d
