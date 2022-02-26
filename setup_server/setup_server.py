import logging
import os
import shutil
import time
import docker

import paramiko
import yaml

from prometheus_wit_client import version, prometheus_config_file_path

logging.basicConfig(level=logging.INFO)
logging.getLogger("paramiko").setLevel(logging.WARNING)


def print_test(ssh):
    _, stdout, _ = ssh.exec_command("ls -al")
    output = ""
    for line in stdout.readlines():
        output = output + line
    print(output)
    return


def config_prometheus(server_list):
    root_dir = os.path.abspath(os.curdir)
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


def run():
    root_dir = os.path.abspath(os.curdir)
    file = open(os.path.join(root_dir, 'list_of_servers.yml'), 'r')
    servers = yaml.safe_load(file)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    port = 8000
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

    for server in servers:
        logging.info("  Processing server {}".format(server.get('hostname')))
        ssh.connect(hostname=server.get('hostname'),
                    port=22,
                    username=server.get('username'),
                    password=server.get('password'))

        get_images_command = "sudo docker container ls --format \"{{.Image}}\""
        _, stdout, stderr = ssh.exec_command(get_images_command)
        images_list = stdout.readlines()
        filtered_var = [image for image in images_list if "prometheus_wit_client" in image]
        is_client_container_running = bool(filtered_var)
        if not is_client_container_running:
            logging.info('Client not running. Starting...')
            run_prometheus_client_command = "sudo docker run --name prometheus_wit_client -d \
                                            -p 8000:8000 -v /run/docker.sock:/run/docker.sock:ro \
                                            --restart always carequinha/prometheus_wit_client:{}" \
                .format(version)
            _, stdout, stderr = ssh.exec_command(run_prometheus_client_command)
            print("Output: {}".format(stdout.readline()))
            print("Errput: {}".format(stderr.readline()))
        else:
            logging.warning('Client already running. Nothing to be done.')
        ssh.close()
    return


if __name__ == '__main__':
    run()
