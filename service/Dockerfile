FROM python:3.8-slim-buster

WORKDIR /app
ENV TZ=America/Sao_Paulo

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "app/main.py"]
