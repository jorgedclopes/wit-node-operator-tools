import paramiko
import yaml


def run():
    file = open('setup_server/list_of_servers.yaml', 'r')
    content = yaml.safe_load(file)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for d in content:
        print(d)
        try:
            ssh.connect(hostname=d.get('hostname'),
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