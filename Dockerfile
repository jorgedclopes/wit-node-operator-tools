FROM python:3.7-slim

WORKDIR /usr/src/app
EXPOSE 8000/tcp
ENV DOCKER_HOST unix:///run/docker.sock

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY prometheus_wit_client .

CMD ["python", "prometheus_wit_client.py"]