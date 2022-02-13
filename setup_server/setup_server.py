import logging
import time

import paramiko
import yaml
from paramiko.ssh_exception import SSHException

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
        logging.warning()
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
    file = open('setup_server/list_of_servers.yaml', 'r')
    content = yaml.safe_load(file)

    print(content)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for d in content:
        print(d)
        try:
            ssh.connect(hostname=d.get('hostname'),
                        port=22,
                        username=d.get('username'),
                        password=d.get('password'))
            logging.info("Connected!")

            initial_setup(ssh)
            ssh.exec_command("sudo reboot")
            print_test(ssh)

            ssh.close()
            logging.info("Connection closed!")

            safe_connect(ssh,
                         hostname=d.get('hostname'),
                         port=22,
                         username=d.get('username'),
                         password=d.get('password'))
        except Exception as e:
            print(e)
            print(type(e))
            raise e
    return


if __name__ == '__main__':
    run()
