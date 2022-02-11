import prometheus_client
import time
import logging
import docker
from typing import List
import re

required_container = 'witnet/witnet-rust'
logging.basicConfig(level=logging.INFO)


def append_to_list(class_list,
                   metric_name,
                   container_name):
    class_list.append(
        prometheus_client.Gauge(
            (metric_name + '_' + container_name).replace('-', '_'),
            metric_name))


def search_from_pattern(string,
                        begin,
                        end):
    try:
        return float(re.search(begin + '(.*)' + end,
                               string)
                     .group(1))
    except Exception as e:
        logging.warning('{e}'.format(e=str(e)))
        logging.warning('Trying to find between {} and {} in {}', begin, end, string)
        return -1


def check_pattern_in_tags(string: str,
                          str_list: List[str]):
    return any(map(lambda el: string in el,
                   str_list))


class WitnetMetrics:
    _container = None
    proposed_block = None
    blocks_in_blockchain = None
    eligibility_times = None
    proposed_commits = None
    accepted_commits = None
    slashed_commits = None
    reputation = None
    eligibility_percentage = None

    def __init__(self, container):
        self._container = container
        self.proposed_block = prometheus_client.Gauge(
            ('Proposed_blocks' + '_' + container.name).replace('-', '_'),
            'Proposed blocks')
        self.blocks_in_blockchain = prometheus_client.Gauge(
            ('Blocks_in_blockchain' + '_' + container.name).replace('-', '_'),
            'Blocks_in_blockchain')
        self.eligibility_times = prometheus_client.Gauge(
            ('Times_eligible' + '_' + container.name).replace('-', '_'),
            'Times_eligible')
        self.proposed_commits = prometheus_client.Gauge(
            ('Proposed_commits' + '_' + container.name).replace('-', '_'),
            'Proposed_commits')
        self.accepted_commits = prometheus_client.Gauge(
            ('Accepted_commits' + '_' + container.name).replace('-', '_'),
            'Accepted_commits')
        self.slashed_commits = prometheus_client.Gauge(
            ('Slashed_commits' + '_' + container.name).replace('-', '_'),
            'Slashed_commits')
        self.reputation = prometheus_client.Gauge(
            ('Reputation' + '_' + container.name).replace('-', '_'),
            'Reputation')
        self.eligibility_percentage = prometheus_client.Gauge(
            ('Eligibility_Percentage' + '_' + container.name).replace('-', '_'),
            'Eligibility_Percentage')

    # Decorate function with metric.
    def process_request(self):
        """Probe the docker information and set the gauges."""

        _, output = self._container.exec_run('witnet node nodeStats')
        logging.debug(output)
        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Proposed blocks: ',
                                                '\n')
        self.proposed_block.set(interesting_value)

        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Blocks included in the block chain: ',
                                                '\n')
        self.blocks_in_blockchain.set(interesting_value)

        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Times with eligibility to mine a data request: ',
                                                '\n')
        self.eligibility_times.set(interesting_value)

        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Proposed commits: ',
                                                '\n')
        self.proposed_commits.set(interesting_value)

        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Accepted commits: ',
                                                '\n')
        self.accepted_commits.set(interesting_value)

        interesting_value = search_from_pattern(output.decode('utf-8'),
                                                'Slashed commits: ',
                                                '\n')
        self.slashed_commits.set(interesting_value)

        _, output_reputation = self._container.exec_run('witnet node reputation')
        interesting_value = search_from_pattern(output_reputation.decode('utf-8'),
                                                'Reputation: ',
                                                ', ')
        self.reputation.set(interesting_value)

        interesting_value = search_from_pattern(output_reputation.decode('utf-8'),
                                                'Eligibility: ',
                                                '%\n')
        self.eligibility_percentage.set(interesting_value)

        logging.info('Metric Updated!')


if __name__ == '__main__':
    logging.info('Starting application.')

    # Start up the server to expose the metrics.
    client = docker.from_env()

    # Assuming the nodes on the server don't change
    interesting_containers = list(filter(lambda el:
                                         check_pattern_in_tags(required_container,
                                                               el.image.tags),
                                         client.containers.list()))

    logging.info(interesting_containers)
    Witnet_metrics_list = [WitnetMetrics(container) for container in interesting_containers]

    logging.info('Starting server')
    prometheus_client.start_http_server(8000)
    # Generate some requests.
    while True:
        if not interesting_containers:
            logging.error('No containers of interest provided')
        for container in Witnet_metrics_list:
            container.process_request()

        logging.info('Metrics refreshed.')
        time.sleep(10)
