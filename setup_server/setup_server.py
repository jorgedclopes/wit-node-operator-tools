import logging
import os
import time

import paramiko
import yaml

from prometheus_wit_client import version

logging.basicConfig(level=logging.INFO)


def safe_connect(ssh: paramiko.SSHClient,
                 hostname,
                 port,
                 username,
                 password):
    try:
        return ssh.connect(hostname=hostname,
                           port=port,
                           username=username,
                           password=password)
    except paramiko.ssh_exception.AuthenticationException as e:
        logging.warning(e)
        time.sleep(1)
        safe_connect(ssh=ssh,
                     hostname=hostname,
                     port=port,
                     username=username,
                     password=password)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        logging.warning(e)
        time.sleep(1)
        safe_connect(ssh=ssh,
                     hostname=hostname,
                     port=port,
                     username=username,
                     password=password)


def initial_setup(ssh: paramiko.SSHClient):
    ssh.exec_command("sudo apt update -y")
    ssh.exec_command("sudo apt install docker.io -y")
    ssh.exec_command("sudo apt install bc -y")
    return


def print_test(ssh):
    _, stdout, _ = ssh.exec_command("ls -al")
    output = ""
    for line in stdout.readlines():
        output = output + line
    print(output)
    return


def run():
    root_dir = os.path.abspath(os.curdir)
    file = open(os.path.join(root_dir, 'list_of_servers.yaml'), 'r')
    servers = yaml.safe_load(file)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for server in servers:
        logging.info("  Processing server {}".format(server.get('hostname')))
        ssh.connect(hostname=server.get('hostname'),
                    port=22,
                    username=server.get('username'),
                    password=server.get('password'))

        get_images_command = "sudo docker container ls --format \"{{.Image}}\""
        _, stdout, stderr = ssh.exec_command(get_images_command)
        images_list = stdout.readlines()
        filtered_var = list(filter(lambda image: "prometheus_wit_client" in image, images_list))
        is_client_container_running = bool(filtered_var)
        if not is_client_container_running:
            logging.info('Client not running. Starting...')
            run_prometheus_client_command = "sudo docker run --name prometheus_wit_client -d \
                                            -p 8000:8000 -v /run/docker.sock:/run/docker.sock:ro \
                                            --restart always carequinha/prometheus_wit_client:{}"\
                .format(version)
            _, stdout, stderr = ssh.exec_command(run_prometheus_client_command)
            print("Output: {}".format(stdout.readline()))
            print("Errput: {}".format(stderr.readline()))
        else:
            logging.warning('Client already running. Nothing to be done.')
        ssh.close()
    return


def reboot_reconnect(server, ssh):
    try:
        ssh.connect(hostname=server.get('hostname'),
                    port=22,
                    username=server.get('username'),
                    password=server.get('password'))
        logging.info("Connected!")

        initial_setup(ssh)
        ssh.exec_command("sudo reboot")
        print_test(ssh)

        ssh.close()
        logging.info("Connection closed!")

        safe_connect(ssh,
                     hostname=server.get('hostname'),
                     port=22,
                     username=server.get('username'),
                     password=server.get('password'))
    except Exception as e:
        print(e)
        print(type(e))
        raise e


if __name__ == '__main__':
    run()
