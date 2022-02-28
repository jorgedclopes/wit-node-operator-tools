import logging
import os
import shutil
from typing import List
import time
import docker

import paramiko
import yaml
import argparse

from prometheus_wit_client import version, prometheus_config_file_path

logging.basicConfig(level=logging.INFO)
logging.getLogger("paramiko").setLevel(logging.WARNING)


def wait_until(some_predicate, timeout, period=0.25, *args, **kwargs):
    must_end = time.time() + timeout
    while time.time() < must_end:
        if some_predicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False


def config_prometheus(server_list: List[str]):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    prometheus_file = open(os.path.join(root_dir, prometheus_config_file_path), 'r')
    prometheus_config = yaml.safe_load(prometheus_file)
    prometheus_file.close()

    logging.info("Prometheus config start.")
    for c in prometheus_config.get('scrape_configs'):
        logging.debug("The job's name is {}".format(c.get("job_name")))
        if c.get("job_name") == 'custom metrics':
            logging.info("Job found!")
            c.get("static_configs")[0]['targets'] = server_list

    logging.debug(prometheus_config)
    logging.info("Prometheus config finish.")
    prometheus_file = open(os.path.join(root_dir, prometheus_config_file_path), 'w')
    yaml.dump(prometheus_config, prometheus_file)
    prometheus_file.close()
    return


def deploy_prometheus_custom_metrics(server: dict,
                                     overwrite: bool):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logging.info("  Processing server {}".format(server.get('hostname')))
    ssh.connect(hostname=server.get('hostname'),
                port=22,
                username=server.get('username'),
                password=server.get('password'))

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
        shutil.copy(os.path.join(root_dir, prometheus_config_file_path),
                    prometheus_dest_dir)
        logging.info("Prometheus config file copied.")

        try:
            client = docker.from_env()
            client.containers.get("prometheus").restart()
            logging.info("Prometheus restarted.")
        except Exception as e:
            logging.warning(e)
            pass

    # TODO: add overwrite server option
    for server in servers:
        deploy_prometheus_custom_metrics(server, overwrite)
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
