# Car Management System

The API Swagger UI with the endpoints documented can be accessed on: `http://localhost:5000/swagger-ui`

I made a Insomnia collection that can be imported on Insomnia to test the API, just needing to adjust the `ids` and set the JWT token, since it expires.

(The `.env` is included to make the testing easier since is a test project)

## Installation

Install `docker` and `docker-compose`

Run:

```bash
docker compose up --build
```

## Usage

Run:

```bash
docker compose up --build
```

## Tests

The tests run when running the project, at the start, but can also executed running:

```bash
docker compose run --rm test
```
