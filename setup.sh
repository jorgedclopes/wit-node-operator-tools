#!/bin/bash

rm -rf ~/.grafana
cp -rf grafana ~/.grafana

rm -rf ~/.alertmanager
cp -rf alertmanager ~/.alertmanager

rm -rf ~/.prometheus
cp -rf prometheus ~/.prometheus