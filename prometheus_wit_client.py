import prometheus_client
import time
import logging
import docker
from typing import List

required_container = 'witnet/witnet-rust'

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


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
        interesting_value = func(output)
        gauge.set(interesting_value)
    time.sleep(10)


def check_pattern_in_tags(string: str, str_list: List[str]):
    return any(map(lambda el: string in el, str_list))


if __name__ == '__main__':
    nodes_gauge_list = []
    # Start up the server to expose the metrics.
    client = docker.from_env()

    # Assuming the nodes on the server don't change
    interesting_containers = list(filter(lambda el:
                                         check_pattern_in_tags(required_container,
                                                               el.image.tags),
                                         client.containers.list()))

    for container in interesting_containers:
        nodes_gauge_list.append(
            prometheus_client.Gauge(
                ('Proposed_blocks_' + container.name).replace('-', '_'),
                'Proposed blocks'))

    print()
    print(interesting_containers)

    prometheus_client.start_http_server(8000)
    # Generate some requests.
    while True:
        process_request(interesting_containers, nodes_gauge_list, lambda x: x)
