# Web Counter

Simple async web counter built with FastAPI to benchmark storage backends and measure RPS.

## Stack

- FastAPI + Uvicorn (async)
- Storage: In-memory, Disk (with fsync), PostgreSQL, Hazelcast AtomicLong, or MongoDB
- Client: httpx for concurrent load testing

## API

```
POST /inc          - Increment counter
GET  /count        - Get current value
GET  /stats        - RPS statistics
```

## Setup

### PostgreSQL Storage

Start PostgreSQL on localhost:5432:

```bash
docker run --name postgres-counter -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### Hazelcast Storage

Start a 3-member Hazelcast cluster with CP Subsystem enabled. See `hazelcast_counter/` for configuration.

## Run Server

```bash
uvicorn app:app --reload
```

## Run Client

```bash
python -m client.count_tester
```

Config: `client/client_config.yaml`

## Benchmark Results (MacBook Pro 2023 on SSD)

- Ram Memory storage: ~1900 RPS
- Disk storage (no fsync): ~1050 RPS
- Disk storage (with fsync): ~900 RPS
- PostgreSQL storage: ~943 RPS
- Hazelcast AtomicLong: ~500 RPS
  - Note: Not fully async, uses `asyncio.to_thread()` + cluster overhead
- MongoDB storage (w=1, j=False): ~1333 RPS
- MongoDB storage (w=1, j=True): ~1087 RPS

## Architecture

- **Storage**: Abstract interface with multiple implementations (in-memory, disk, PostgreSQL, Hazelcast, MongoDB)
- **Middleware**: Request tracking for RPS calculation
- **Domain**: Pydantic models for type safety
- **Client**: Async concurrent load tester (10 clients, 10k requests)
