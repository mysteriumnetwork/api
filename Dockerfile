FROM python:3.6

WORKDIR /code

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

HEALTHCHECK --interval=5s --timeout=5s --retries=15\
    CMD curl -f http://localhost || exit 1

ENTRYPOINT ["python", "server.py"]
