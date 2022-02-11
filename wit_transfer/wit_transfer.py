import logging
import docker
import sys

logging.basicConfig(level=logging.INFO)

# HOW TO CALL
# python wit_transfer.py __container_name__ __wit_amount__
if __name__ == '__main__':
    logging.info('Starting application.')

    # Start up the server to expose the metrics.
    client = docker.from_env()

    if len(sys.argv) != 3:
        logging.error("Wrong number of arguments.")
        raise ValueError("Wrong number of arguments.")

    name = sys.argv[1]
    wit_amount = None
    try:
        wit_amount = int(sys.argv[2])
    except ValueError as e:
        raise ValueError('Amount of wit is not a number.')

    f = open('list_of_wallets.txt', 'r')
    address_list = f.read().split('\n')

    fee = 1
    container = client.containers.get(name)

    logging.info('Starting transfers.')
    for address in address_list:
        command = "witnet node send --fee={} --value={} --address={}".format(fee, wit_amount * 10**9, address)
        print("Command - {}".format(command))
        # container.exec_run(command)

    logging.info('Transfers completed.')
    print(container.exec_run("pwd"))
