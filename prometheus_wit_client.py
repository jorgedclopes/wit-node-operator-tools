import prometheus_client
import time
import logging
import docker
from typing import List
import re

import singleton

required_container = 'witnet/witnet-rust'

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def append_to_list(class_list, metric_name, container_name):
    class_list.append(
        prometheus_client.Gauge(
            (metric_name + '_' + container_name).replace('-', '_'),
            metric_name))


@singleton
class WitnetMetrics:
    proposed_blocks_list = []
    blocks_in_blockchain_list = []
    eligible_list = []
    proposed_commits_list = []
    accepted_commits_list = []
    slashed_commits_list = []
    reputation_list = []

    def __init__(self, container_list):
        for container in container_list:
            WitnetMetrics.proposed_blocks_list.append(
                prometheus_client.Gauge(
                    ('Proposed_blocks_' + container.name).replace('-', '_'),
                    'Proposed blocks'))
            append_to_list(WitnetMetrics.proposed_blocks_list,
                           'Proposed_blocks',
                           container.name)
            append_to_list(WitnetMetrics.blocks_in_blockchain_list,
                           'Blocks_in_blockchain',
                           container.name)
            append_to_list(WitnetMetrics.eligible_list,
                           'Times_elegible',
                           container.name)
            append_to_list(WitnetMetrics.proposed_commits_list,
                           'Proposed_commits',
                           container.name)
            append_to_list(WitnetMetrics.accepted_commits_list,
                           'Accepted_commits',
                           container.name)
            append_to_list(WitnetMetrics.slashed_commits_list,
                           'Slashed_commits',
                           container.name)
            append_to_list(WitnetMetrics.reputation_list,
                           'Reputation_list',
                           container.name)


# Decorate function with metric.
def process_request(container_list,
                    gauge_list,
                    func):
    """A dummy function that sets the gauge."""

    if not container_list:
        logger.error('No containers of interest provided')

    for c, gauge in zip(container_list, gauge_list):
        _, output = c.exec_run('witnet node nodeStats')
        logger.debug(output)
        interesting_value = func(output.decode('utf-8'), 'Proposed blocks: ', '\n')
        gauge.set(interesting_value)
    time.sleep(10)


def search_from_pattern(string, begin, end):
    try:
        return int(re.search(begin + '(.*)' + end, string).group(1))
    except:
        return -1


def check_pattern_in_tags(string: str, str_list: List[str]):
    return any(map(lambda el: string in el, str_list))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    client = docker.from_env()

    # Assuming the nodes on the server don't change
    interesting_containers = list(filter(lambda el:
                                         check_pattern_in_tags(required_container,
                                                               el.image.tags),
                                         client.containers.list()))

    WitnetMetrics(interesting_containers)

    print()
    print(interesting_containers)

    prometheus_client.start_http_server(8000)
    # Generate some requests.
    while True:
        process_request(interesting_containers,
                        WitnetMetrics.proposed_blocks_list,
                        search_from_pattern)
