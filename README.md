# wit-node-operator-tools

Compilation of tools that will help manage Witnet nodes.

Among them are:
- multi-node server setup
- node setup
- transfer of Witnet tokens out of servers

This project is still in very premature stage.

### Project Structure

- bash_scripts\
assorted collection of scripts in bash

- grafana\
configurations for the grafana deployment

- prometheus\
configurations for the prometheus deployment

- prometheus_wit_client\
custom prometheus server with custom metrics specific to the Witnet node operation

- setup_server\
automation to deploy the prometheus custom metric container to all the servers in the configurations file

### Security Statement
#### Why do we need server passwords and how we use them?
Passwords are used to deploy the prometheus custom metric server to each of the servers you have. They are only used in 'setup_server.py'.

This is a shortcoming of the project