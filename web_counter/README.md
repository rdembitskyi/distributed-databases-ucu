# Web Counter

Simple async web counter built with FastAPI to benchmark storage backends and measure RPS.

## Stack

- FastAPI + Uvicorn (async)
- Storage: In-memory or Disk (with fsync)
- Client: httpx for concurrent load testing

## API

```
POST /inc          - Increment counter
GET  /count        - Get current value
GET  /stats        - RPS statistics
```

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

- Memory storage: ~1900 RPS
- Disk storage (no fsync): ~1050 RPS  
- Disk storage (with fsync): ~900 RPS

## Architecture

- **Storage**: Abstract interface with in-memory and disk implementations
- **Middleware**: Request tracking for RPS calculation
- **Domain**: Pydantic models for type safety
- **Client**: Async concurrent load tester (10 clients, 10k requests)
