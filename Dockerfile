FROM python:3.6

WORKDIR /code

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

ENTRYPOINT ["python", "server.py"]
