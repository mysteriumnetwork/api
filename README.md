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

### Pre-requisites

Follow [Google cloud guide](https://cloud.google.com/python/setup) to setup python development environment.

### Testing

Install the requirements using pip
```
$ pip install -r requirements.txt
```

To execute tests in docker container:
- Run:
```bash
tests/run_tests
```

(Optional)

After that test database will be kept running in the background, so you can execute.
To do that, you need to do additional steps:
- Ensure that python 3.6+ is installed globally (`python --version`)
- Add ENV variables:
```bash
DB_HOST=localhost:33062
DB_NAME=myst_api
DB_USER=myst_api
DB_PASSWORD=myst_api
```
- Run tests from IDE or bash:
```bash
bin/test
```

### Linter

To run linter:
```bash
bin/lint
```

### Database schema changes

To change database schema:

- Change schema in `models.py` (i.e. add new table, column or change existing schema)
- Run `bin/db-migrate` to create migration script
- Check created script manually to ensure it is correct.
It sometimes fail, so you might need to modify it.
- Run `bin/db-upgrade` to apply migration

That's it!
As a bonus point, you can try running `bin/db-migrate` again.
It should not create a new migration file - if it does, that means previous migration is incorrect and should be fixed.
