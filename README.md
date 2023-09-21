# user_manager

## Prerequisites
* docker engine (tested with 20.10.7, build f0df350)
* docker-compose v2 (tested with v2.1.0)

## Installation
Run `make prepare_env` (it will simply copy default config files and build the main image).

The service runs on port 7531 (mapped to 7531), and it relies on redis and mysql, both of them not forwarded to the host by default.

In order to change the port please edit `docker-compose.yml` and `config/application.json`.

## Usage
* `make start`
* `make stop`
* `make restart`

The above will affect all services (user_manager, local_mysql and local_redis).

Mysql is provisioned on first spin up, the relevant file is `mysql/entrypoint/sql_init.sql`.

## Endpoints
There's an OpenAPI-compliant yaml file at top level (`open_api.yaml`)

## Tests
Run `make test`

N.B. it's just one test...

## Missing pieces
In no particular order:
* consistent type hints
* comments
* Improved validation for datetimes (i.e. not in the future, from / to order, etc.)
* Concept of session (there's only one table now, and login simply updates the last_login colum)
* SQLAlchemy (or any ORM really) models
* Proper search functionality
* More unit tests
* Functional tests
