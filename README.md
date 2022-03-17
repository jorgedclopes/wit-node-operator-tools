# wit-node-operator-tools

Compilation of tools to monitor Witnet nodes.

### Basic Setup - How To

Requirements:
 - docker-compose
 - pip3

Setup:

1) from this project's `root directory`, open the file `/setup_server/list_of_servers_example.yml`
2) Keeping the yaml layout pattern present, edit it with the list of servers and respective ssh credentials
3) save it under `/setup_server/list_of_servers.yml`. For security reasons this file doesn't exist from the get go in this repo
4) run `./setup.sh`

You're all set. A few minutes after the setup runs, give the system some time (~5-10 min)
for prometheus and grafana to discover all data sources.
Grafana will already come with a default dashboard specific to the Witnet node operations.

To access the Grafana dashboard open a browser at `http://localhost:3000` or replace `localhost` by the appropriate IP address.
Grafana default credentials are `user:pass = admin:admin`. The password can be changed at any time after login. 

### Project Structure

- bash_scripts\
assorted collection of scripts in bash (status: draft)

- grafana\
configurations for the grafana deployment

- prometheus\
configurations for the prometheus deployment

- prometheus_wit_client\
custom prometheus server with custom metrics specific to the Witnet node operation

- setup_server\
automation to deploy the prometheus custom metric container to all the servers in the configurations file

### Security Concerns & Full Disclosure
<ins>Why do I need server passwords and how does the code in this project use them?</ins>

Passwords are used to deploy the prometheus custom metric server to each of the servers you have. They are only used in `setup_server/setup_server.py`.  
Unless something goes wrong with the setup, this is a one time operation.

<ins>Who has access to my sensitive data?</ins>

Only people with the credentials to enter the machine where you setup this Prometheus+Grafana project will have access to this data.  
Prometheus_wit_client containers expose data and they are accessible from anywhere but that data is not sensitive.
It is not possible to manipulate/compromise your nodes with the information exposed.  
Prometheus and Grafana communication is setup with basic authentication using a password created at setup.
This ensures the password is, for all practical purposes, unique.