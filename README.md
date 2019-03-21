# Mysterium Network API

[![Build Status](https://travis-ci.org/MysteriumNetwork/api.svg?branch=master)](https://travis-ci.org/MysteriumNetwork/api)
[![pyVersion36](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/)

API for Node & Client

## Setup

- Start docker containers in background:
```bash
docker-compose up -d --build
```

- Wait ~10s for database to setup.

- Run database migrations:
```bash
docker-compose exec api bin/db-upgrade
```

- API service should be running on http://127.0.0.1:8001
- Dashboard on http://127.0.0.1:8002

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
