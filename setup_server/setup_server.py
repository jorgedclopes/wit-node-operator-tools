import logging
import os
import shutil
import string

import numpy as np
from typing import List
import time
import docker

import paramiko
import yaml
import argparse
import bcrypt

from prometheus_wit_client import version

prometheus_config_origin_file_path = '../prometheus/.prometheus.yml'
prometheus_config_dest_file_path = '../prometheus/prometheus.yml'
prometheus_web_file_path = '../prometheus/web.yml'
grafana_config_origin_file_path = '../grafana/provisioning/datasources/.datasource.yml'
grafana_config_dest_file_path = '../grafana/provisioning/datasources/datasource.yml'

logging.basicConfig(level=logging.INFO)
logging.getLogger("paramiko").setLevel(logging.WARNING)


def generate_random_password(length: int,
                             seed: int) -> str:
    characters = list(string.ascii_letters + string.digits)
    np.random.seed(seed=seed)
    np.random.shuffle(characters)
    password = ''.join(np.random.choice(characters) for _ in range(length))
    return password


def generate_seeded_password(length: int) -> str:
    return generate_random_password(length,
                                    np.random.randint(2 ** 32))


def wait_until(some_predicate, timeout, period=0.25, *args, **kwargs):
    must_end = time.time() + timeout
    while time.time() < must_end:
        if some_predicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False


def config_prometheus(server_list: List[str]):
    root_dir = os.path.abspath(os.path.dirname(__file__))

    password = generate_seeded_password(128)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    with open(os.path.join(root_dir, prometheus_config_origin_file_path), 'r') as prometheus_origin_file:
        prometheus_config = yaml.safe_load(prometheus_origin_file)
        prometheus_origin_file.close()

        logging.info("Prometheus config start.")
        for c in prometheus_config.get('scrape_configs'):
            logging.debug("The job's name is {}".format(c.get("job_name")))
            if c.get("job_name") == 'custom metrics':
                logging.info("Job found!")
                c['static_configs'][0]['targets'] = server_list
            if c.get("job_name") == 'prometheus':
                c['basic_auth'] = {'username': 'admin',
                                   'password': password}

        logging.debug(prometheus_config)
        logging.info("Prometheus config finish.")
        with open(os.path.join(root_dir, prometheus_config_dest_file_path), 'w') as prometheus_dest_file:
            yaml.dump(prometheus_config, prometheus_dest_file)

    # Setup prometheus/grafana security
    web_data = {'basic_auth_users': {'admin': hashed_password.decode()}}
    with open(os.path.join(root_dir, prometheus_web_file_path), 'w') as web_file:
        yaml.dump(web_data, web_file, default_flow_style=False)

    with open(os.path.join(root_dir, grafana_config_origin_file_path)) as dash_origin_file:
        grafana_dashboard_config = yaml.safe_load(dash_origin_file)

        grafana_dashboard_config['datasources'][0]['basicAuth'] = True
        grafana_dashboard_config['datasources'][0]['basicAuthUser'] = 'admin'
        grafana_dashboard_config['datasources'][0]['secureJsonData']['basicAuthPassword'] = password

        grafana_dashboard_config['datasources'][0].pop('jsonData')
        grafana_dashboard_config['datasources'][0].pop('basicAuthPassword')
        grafana_dashboard_config['datasources'][0].pop('database')
        grafana_dashboard_config['datasources'][0].pop('password')
        grafana_dashboard_config['datasources'][0].pop('user')
        grafana_dashboard_config['datasources'][0].pop('withCredentials')

        with open(os.path.join(root_dir, grafana_config_dest_file_path), 'w') as dash_dest_file:
            yaml.dump(grafana_dashboard_config, dash_dest_file, explicit_start=True)

    return


def deploy_prometheus_custom_metrics(server: dict,
                                     overwrite: bool):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logging.info("  Processing server {}".format(server.get('hostname')))
    ssh.connect(hostname=server.get('hostname'),
                port=22,
                username=server.get('username'),
                password=server.get('password'),
                timeout=15)

    is_client_container_running = poll_container(ssh)

    if is_client_container_running and overwrite:
        _, stdout, stderr = ssh.exec_command('sudo docker stop prometheus_wit_client')
        for out in stdout.readlines():
            logging.info("Stop Output: {}".format(out))
        for err in stderr.readlines():
            logging.debug("Stop Errput: {}".format(err))

        _, stdout, stderr = ssh.exec_command('sudo docker container rm prometheus_wit_client')
        for out in stdout.readlines():
            logging.info("rm Output: {}".format(out))
        for err in stderr.readlines():
            logging.debug("rm Errput: {}".format(err))
        is_client_container_running = False
        logging.info("Deleted prometheus container. Preparing to redeploy.")
        wait_until(lambda s: not poll_container(s), 30, 0.25, ssh)

    if not is_client_container_running:
        logging.info('Client not running. Starting...')
        _, stdout, stderr = ssh.exec_command('sudo docker pull carequinha/prometheus_wit_client:{}'
                                             .format(version))
        for out in stdout.readlines():
            logging.debug("Pull Output: {}".format(out))
        for err in stderr.readlines():
            logging.debug("Pull Errput: {}".format(err))
        run_prometheus_client_command = "sudo docker run --name prometheus_wit_client -d \
                                            -p 8000:8000 -v /run/docker.sock:/run/docker.sock:ro \
                                            --restart always carequinha/prometheus_wit_client:{}" \
            .format(version)
        _, stdout, stderr = ssh.exec_command(run_prometheus_client_command)
        for out in stdout.readlines():
            logging.info("Run Output: {}".format(out))
        for err in stderr.readlines():
            logging.debug("Run Errput: {}".format(err))
    else:
        logging.warning('Client already running. Nothing to be done.')

    ssh.close()
    return


def poll_container(ssh):
    get_images_command = "sudo docker container ls -a --format \"{{.Image}}\""
    _, stdout, stderr = ssh.exec_command(get_images_command)
    images_list = stdout.readlines()
    filtered_var = [image for image in images_list if "prometheus_wit_client" in image]
    is_client_container_running = bool(filtered_var)
    return is_client_container_running


def run(port: int,
        list_of_servers: str,
        overwrite: bool):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    servers_file_path = os.path.join(root_dir, list_of_servers)
    os.path.isfile(servers_file_path)
    file = open(servers_file_path, 'r')
    servers = yaml.safe_load(file)

    server_list = ["{}:{}".format(s.get('hostname'), port) for s in servers]
    logging.info(server_list)

    config_prometheus(server_list)

    prometheus_dest_dir = os.path.expanduser("~/.prometheus/")
    if os.path.isdir(prometheus_dest_dir):
        shutil.copy(os.path.join(root_dir, prometheus_config_dest_file_path),
                    prometheus_dest_dir)
        logging.info("Prometheus config file copied.")

        try:
            client = docker.from_env()
            client.containers.get("prometheus").restart()
            logging.info("Prometheus restarted.")
        except Exception as e:
            logging.warning(e)
            pass

    for server in servers:
        try:
            deploy_prometheus_custom_metrics(server, overwrite)
        except Exception as e:
            logging.error(e)
            logging.error("Failed to process the deployment of prometheus custom metric server in {}."
                          .format(server.get('hostname')))
            continue
    return


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Setup a list of servers. File is passed as an argument.')
    arg_parser.add_argument('--config', action='store',
                            dest='list_of_servers', default='list_of_servers.yml',
                            help='Pass the relative file path with the list of servers. Default: list_of_servers.yml')
    arg_parser.add_argument('--overwrite-servers', action='store_true',
                            dest='overwrite_servers', default=False,
                            help='Overwrite the server if there\'s already one deployed')
    arguments = arg_parser.parse_args()
    run(8000, arguments.list_of_servers, arguments.overwrite_servers)
