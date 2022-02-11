import paramiko
import yaml


def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='45.130.104.48',
                port=22,
                username='admin',
                password='!Wolfgang1791')

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls -a')
    print(type(ssh_stdout))
    print(ssh_stdout.read().decode('utf-8'))
    return


if __name__ == '__main__':
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
    # run()
