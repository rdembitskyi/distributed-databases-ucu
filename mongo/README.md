# MongoDB Queries

A collection of MongoDB query examples using PyMongo: CRUD operations, aggregation pipelines, references, embedded documents, and capped collections.

## Setup

### 1. Start MongoDB via Docker Compose

```bash
cd mongo
docker-compose up -d
```

This starts:
- **MongoDB** on `localhost:27017`
- **Mongo Express** (web UI) on `http://localhost:8081`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run queries

```bash
cd queries

# Items: CRUD, aggregation, filtering
python queries.py

# Orders: references, embedded docs, $lookup joins
python queries_orders.py

# Reviews: capped collection (max 5 docs)
python queries_reviews.py
```

## Query Files

- **`queries.py`** — item CRUD, `$and`/`$or`/`$in` filters, `$group` aggregation, `$exists`, `updateMany` with `$inc`/`$set`
- **`queries_orders.py`** — orders with embedded customers and referenced items, `$lookup` joins, `$push`/`$pull` array operations
- **`queries_reviews.py`** — capped collection demo, auto-eviction of old documents