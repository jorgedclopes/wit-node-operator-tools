import prometheus_client
import random
import time
import logging
import docker
from typing import List
from functools import reduce

required_container = 'witnet/witnet-rust'

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
g = prometheus_client.Gauge('my_in_progress_requests', 'Description of gauge')
g2 = prometheus_client.Gauge('my_in_progress_requests2', 'Description of gauge')


# Decorate function with metric.
def process_request():
    """A dummy function that sets the gauge."""
    output = random.randint(0, 10)
    g.set(output)
    logger.info("Random number generated = %s", output)
    output = random.randint(0, 10)
    g2.set(output)
    logger.info("Random number generated = %s", output)
    time.sleep(10)


def check_pattern_in_tags(string: str, str_list: List[str]):
    return any(map(lambda el: string in el, str_list))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    client = docker.from_env()
    for container in client.containers.list():
        is_witnet_node = check_pattern_in_tags(required_container, container.image.tags)
        print(container.image.tags)
        print(is_witnet_node)
        print(container.name)
    # print(docker_result.stderr)
    print()
    exit()
    prometheus_client.start_http_server(8000)
    # Generate some requests.
    while True:
        process_request()
