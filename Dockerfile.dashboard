FROM python:3.6

WORKDIR /code/dashboard

ADD dashboard/requirements.txt .
RUN pip install -r requirements.txt

ADD dashboard /code/dashboard
ADD models.py /code/models.py
ADD queries.py /code/queries.py
ADD api /code/api

HEALTHCHECK --interval=5s --timeout=5s --retries=15\
    CMD curl -f http://localhost/ping || exit 1

ENTRYPOINT ["python", "server.py"]
