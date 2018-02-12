# Mysterium Network API

API for Node & Client

## Setup [![pyVersion27](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7/)

- Setup `settings.py` file:
    ```bash
    DB_HOST = 'db'
    DB_NAME = 'myst_api'
    USER = 'root'
    PASSWD = 'root'
    ```

- Start docker containers in background:

    ```bash
    docker-compose up -d
    ```

- Wait ~10s for database to setup.

- Run database migrations:

    ```bash
    docker-compose exec -e FLASK_APP=app.py web flask db upgrade
    ```

- Service should be running on http://127.0.0.1:5000/

## Development

Install the requirements using pip
```
$ pip install -r requirements.txt
```

To execute tests, start api service in background and run:
```bash
python -m unittest discover
```

To run linter:
```bash
./lint
```
