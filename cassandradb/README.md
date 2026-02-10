# Cassandra Queries

A collection of Cassandra query examples using the Python driver: table design, secondary indexes, aggregations, collection operations, TTL, and WRITETIME.

## Setup

### 1. Start Cassandra via Docker Compose

```bash
cd cassandradb
docker-compose up -d
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create tables and seed data

```bash
python client/data/create_tables.py
python client/data/seed_data.py
```

### 4. Run queries

```bash
cd queries

# Items: CRUD, filtering by category/price/producer, MAP property queries
python query_items.py

# Orders: per-customer queries, date ranges, COUNT, MAX, GROUP BY, WRITETIME
python query_orders.py

# Mutations: add/remove items from orders (SET operations), TTL inserts
python mutate_orders.py
```

## Query Files

- **`query_items.py`** — DESCRIBE, category/price/name filtering, `CONTAINS KEY`, `properties[key] = value`
- **`query_orders.py`** — per-customer ordering, `CONTAINS` on SET, date range + COUNT, `MAX` with `GROUP BY`, `WRITETIME`
- **`mutate_items.py`** — item mutations
- **`mutate_orders.py`** — add/remove items via `SET +/-`, read-then-write price update, `INSERT ... USING TTL`