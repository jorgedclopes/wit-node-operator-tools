from prometheus_client import start_http_server, Gauge
import random
import time
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
g = Gauge('my_in_progress_requests', 'Description of gauge')
g2 = Gauge('my_in_progress_requests2', 'Description of gauge')


# Decorate function with metric.
def process_request():
    """A dummy function that sets the gauge."""
    output = random.randint(0, 10)
    g.set(output)
    logger.info("Random number generated = %s", output)
    output = random.randint(0, 10)
    g2.set(output)
    # sudo docker exec witnet-1 witnet node balance
    logger.info("Random number generated = %s", output)
    time.sleep(10)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        process_request()
