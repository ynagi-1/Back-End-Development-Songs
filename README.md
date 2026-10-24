# Back-End-Development-Songs

Flask REST API for the band website. Based on the official IBM Skills Network
`hvlga-Back-End-Development-Songs` template.

## Development environment

Use Python 3.9 in an isolated virtual environment. The course Cloud IDE also
provides `bash ./bin/setup.sh` to initialize its Linux environment.

```sh
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
python -m flask run --host 0.0.0.0 --port 8080
```

On Windows, activate `.venv/Scripts/activate`. Python 3.9 on Windows can install
a compatible binary dependency with `pip install -r requirements.txt greenlet==3.1.1`.

## API

- GET /health: 200 with status OK.
- GET /count: 200 with the resource count.
- GET /song: list all records.
- GET /song/id: return a record, or 404 if absent.
- POST /song: create a record (201), or reject a duplicate id (302).
- PUT /song/id: update an existing record, or return 404 if absent.
- DELETE /song/id: delete a record (204), or return 404 if absent.

Invalid JSON and conflicting resource ids return 400.

## Container

```sh
docker build -t songs .
docker run --rm -p 8080:8080 songs
```

## MongoDB configuration

Start a MongoDB service before importing the application. Set MONGODB_SERVICE
(default 127.0.0.1), MONGODB_PORT (default 27017), and optionally MONGODB_USERNAME
and MONGODB_PASSWORD. MONGODB_URI overrides the constructed connection URI.
MONGODB_DATABASE defaults to songs. Use environment variables for credentials;
credentials are never logged or committed. With Docker, pass database connection
variables using -e and use the MongoDB service name on the container network.

The original twenty songs are seeded only if the collection is empty. A unique
index prevents duplicate song ids. Existing data survives restarts. PUT returns
201 with the updated record, or 200 if unchanged. The health endpoint verifies a
database ping. Deploy MongoDB and Songs to OpenShift and expose port 8080.
