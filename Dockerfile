# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
ENV TZ=America/Sao_Paulo
ENV FLASK_APP process-pag.py

RUN apt-get update && apt-get -y upgrade 
RUN apt-get -y install curl

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY cert.pem cert.pem
COPY key.pem key.pem
COPY . .

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f https://api.tickpass.com.br/ || exit 1

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--cert=cert.pem", "--key=key.pem"]
