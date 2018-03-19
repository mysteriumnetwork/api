# Mysterium Network API

[![Build Status](https://travis-ci.org/MysteriumNetwork/api.svg?branch=master)](https://travis-ci.org/MysteriumNetwork/api)
[![pyVersion27](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7/)

API for Node & Client

## Setup

- Start docker containers in background:
```bash
docker-compose up -d
```

- Wait ~10s for database to setup.

- Run database migrations:
```bash
docker-compose exec api bin/db-migrate
```

- Service should be running on http://127.0.0.1:8001/

## Development

Install the requirements using pip
```
$ pip install -r requirements.txt
```

To execute tests, start api service in background and run:
```bash
bin/test
```

To run linter:
```bash
bin/lint
```
