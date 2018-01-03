FROM python:2.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install -r requirements_prod.txt
CMD ["python", "server.py"]
