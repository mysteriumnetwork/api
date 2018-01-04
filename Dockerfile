FROM python:2.7

ADD requirements.txt /code/requirements.txt
ADD requirements_prod.txt /code/requirements_prod.txt
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install -r requirements_prod.txt

ADD . /code
CMD ["python", "server.py"]
