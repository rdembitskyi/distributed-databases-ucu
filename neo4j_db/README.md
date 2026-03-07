# Neo4j

Graph database with a simple e-commerce model: customers, orders, and items linked by relationships (PLACED, CONTAINS, VIEWED).

## Setup

Start Neo4j in Docker:

```bash
docker-compose up -d
```

This runs Neo4j on `bolt://localhost:7687` with the browser UI at `http://localhost:7474`.

Credentials: `neo4j` / `password`.

## Seed Data

```bash
python -m queries.seed
```

Creates items (football gear), customers (Italian football legends), orders with CONTAINS relationships, and VIEWED edges.

## Queries

```bash
python -m queries.queries
```

Demonstrates graph-specific queries:
- Find items in an order / calculate order total
- Find orders and items by customer
- Total items and total spent per customer
- Most purchased items across all orders
- Items frequently bought together (graph traversal)
- Customers who bought a specific item
- Items viewed but not purchased (recommendation use case)

## Requirements

```bash
pip install -r requirements.txt
```