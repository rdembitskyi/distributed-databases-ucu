# Massive Insert - Concurrent Update Tests

This project demonstrates different concurrency control strategies for handling concurrent database updates in PostgreSQL.

## Overview

Tests concurrent updates to a counter field using 10 parallel clients, each performing 10,000 increments. The goal is to demonstrate race conditions and various solutions.

## Test Scenarios

### 1. **Lost Updates** (Read-Update-Write)
- **Strategy**: `SELECT` → Increment in app → `UPDATE`
- **Isolation Level**: READ COMMITTED
- **Result**: **Race condition - lost updates occur**
- **Why**: Multiple threads read the same value before any update

### 2. **Lost Updates with SERIALIZABLE**
- **Strategy**: Same as #1 but with SERIALIZABLE isolation + retry logic
- **Isolation Level**: SERIALIZABLE
- **Result**: No lost updates (with retry)
- **Why**: Database detects conflicts and aborts transactions; application retries

### 3. **In-Place Update** (Atomic Increment)
- **Strategy**: `UPDATE count = count + 1`
- **Isolation Level**: READ COMMITTED
- **Result**: No lost updates
- **Why**: Database performs read-increment-write atomically with row-level locking

### 4. **SELECT FOR UPDATE** (Pessimistic Locking)
- **Strategy**: `SELECT ... FOR UPDATE` → Increment → `UPDATE`
- **Isolation Level**: READ COMMITTED
- **Result**: No lost updates
- **Why**: Row locked at SELECT time; other transactions wait

### 5. **Optimistic Concurrency Control**
- **Strategy**: Read `(count, version)` → `UPDATE WHERE version = old_version`
- **Isolation Level**: READ COMMITTED
- **Result**: No lost updates
- **Why**: Version field prevents conflicting updates; retry on conflict

## Database Schema

```sql
CREATE TABLE user_count (
    user_id BIGINT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 0
);
```

## Running Tests

1. **Start PostgreSQL**:
   ```bash
   docker-compose up --build
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Run tests**:
   ```bash
   python main.py
   ```

## Project Structure

```
massive_insert/
├── db_queries/
│   ├── concurrent_update.py    # Main test wrapper + query strategies
│   └── shared.py               # Shared database utilities
├── migrations/
│   └── create_user_count.py    # Table creation migration
├── main.py                     # Test runner
├── docker-compose.yml          # PostgreSQL 18 setup
└── requirements.txt            # Python dependencies
```

## Key Takeaways

| Strategy | Locks | Conflicts | Performance           | Complexity |
|----------|-------|-----------|-----------------------|------------|
| Read-Update-Write | None | Not detected | Fast                  | Low (but wrong!) |
| SERIALIZABLE | DB-level | At commit | Slo                   | Medium |
| Atomic Increment | Row-level | None | Fast                  | Low |
| SELECT FOR UPDATE | Row-level | At SELECT | Slower (blocking)     | Low |
| Optimistic Locking | App-level | At UPDATE | Fast (if rare conflicts) | Medium |

## Best Practices

- **Use atomic operations** (`UPDATE count = count + 1`) when possible
- **Use SELECT FOR UPDATE** when you need to read and update with complex logic
- **Use optimistic locking** for distributed systems or when conflicts are rare
- **Use SERIALIZABLE** for complex multi-row consistency requirements
