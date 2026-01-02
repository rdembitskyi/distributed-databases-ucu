# Hazelcast Distributed Counter

Distributed counter implementations using Hazelcast IMDG to demonstrate concurrency control patterns and compare performance under high-contention scenarios.

## Overview

This project implements a distributed counter using multiple approaches:
1. **Distributed Map** (AP - Available + Partition tolerant)
   - Naive implementation (demonstrates race conditions)
   - Pessimistic locking (distributed locks)
   - Optimistic locking (Compare-And-Swap)
2. **AtomicLong** (CP - Consistent + Partition tolerant using Raft consensus)

## Architecture

### Distributed Map (`distributed_map.py`)

Uses Hazelcast's AP distributed map with three concurrency strategies:

#### 1. Naive (Race Conditions)
```python
current_value = distributed_map.get(COUNTER_KEY)
distributed_map.put(COUNTER_KEY, current_value + 1)
```
- **No synchronization**
- **Lost updates expected** - demonstrates why atomicity matters
- Fastest but incorrect under concurrent access

#### 2. Pessimistic Locking
```python
distributed_map.lock(COUNTER_KEY)
try:
    current_value = distributed_map.get(COUNTER_KEY)
    distributed_map.put(COUNTER_KEY, current_value + 1)
finally:
    distributed_map.unlock(COUNTER_KEY)
```
- **Distributed lock** per operation
- **Correct but slow** - serializes all updates
- High lock contention with many processes

#### 3. Optimistic Locking (CAS)
```python
while True:
    current_value = distributed_map.get(COUNTER_KEY)
    new_value = current_value + 1
    if distributed_map.replace_if_same(COUNTER_KEY, current_value, new_value):
        break
```
- **Compare-And-Swap** (atomic conditional replace)
- **Correct and faster** than pessimistic locking
- Retries on conflict (optimistic approach)

### AtomicLong CP Subsystem (`atomic_long.py`)

Uses Hazelcast's CP Subsystem with Raft consensus:

```python
atomic_long = client.cp_subsystem.get_atomic_long(COUNTER_KEY)
atomic_long.increment_and_get().result()
```

- **Strongly consistent** (CP guarantees via Raft)
- **Atomic operations** - no race conditions possible
- Requires 3+ cluster members for quorum
- Survives leader failures with automatic failover

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Hazelcast Cluster

For **Distributed Map** (AP mode), you can use 1+ members:

```bash
docker network create hazelcast-network

docker run \
    --name hazelcast-member-1 \
    --network hazelcast-network \
    -p 5701:5701 \
    hazelcast/hazelcast:5.1.7
```

For **AtomicLong** (CP mode), you need **3+ members** with CP Subsystem enabled:

```bash
# Member 1
docker run \
    --name hazelcast-member-1 \
    --network hazelcast-network \
    -e JAVA_OPTS="-Dhazelcast.config=/opt/hazelcast/config/hazelcast.yaml" \
    -v $(pwd)/hazelcast.yaml:/opt/hazelcast/config/hazelcast.yaml \
    -p 5701:5701 \
    hazelcast/hazelcast:5.1.7

# Member 2
docker run \
    --name hazelcast-member-2 \
    --network hazelcast-network \
    -e JAVA_OPTS="-Dhazelcast.config=/opt/hazelcast/config/hazelcast.yaml" \
    -v $(pwd)/hazelcast.yaml:/opt/hazelcast/config/hazelcast.yaml \
    -p 5702:5701 \
    hazelcast/hazelcast:5.1.7

# Member 3
docker run \
    --name hazelcast-member-3 \
    --network hazelcast-network \
    -e JAVA_OPTS="-Dhazelcast.config=/opt/hazelcast/config/hazelcast.yaml" \
    -v $(pwd)/hazelcast.yaml:/opt/hazelcast/config/hazelcast.yaml \
    -p 5703:5701 \
    hazelcast/hazelcast:5.1.7
```

## Running the Tests

### Distributed Map

```bash
python distributed_map.py
```

Change the `target_func` in the code to test different implementations:
```python
target_func = increment_counter_naive              # Race conditions
target_func = increment_counter_pessimistic_lock   # Distributed locks
target_func = increment_counter_optimistic_lock    # Compare-And-Swap
```

### AtomicLong

```bash
python atomic_long.py
```

## Test Configuration

- **Processes**: 10 concurrent processes
- **Iterations**: 10,000 increments per process
- **Expected result**: 100,000 (10 × 10,000)

## Expected Results

| Implementation | Correctness | Performance | Lost Updates |
|----------------|-------------|-------------|--------------|
| Naive | ❌ Incorrect | Fastest | High (30-70k lost) |
| Pessimistic Lock | ✅ Correct | Slow | 0 |
| Optimistic Lock (CAS) | ✅ Correct | Moderate | 0 |
| AtomicLong (CP) | ✅ Correct | Moderate | 0 |

## Key Learnings

1. **Race Conditions**: Naive get-modify-put causes lost updates under concurrent access
2. **Pessimistic vs Optimistic**: Locks serialize access; CAS allows parallelism with retries
3. **AP vs CP**: Distributed Map (AP) for availability; AtomicLong (CP) for strong consistency
4. **Raft Consensus**: CP Subsystem uses Raft for leader election and data replication
5. **Failover**: CP Subsystem survives member failures via automatic leader re-election

## Configuration Files

- `hazelcast.yaml` - Hazelcast cluster configuration with CP Subsystem settings
- `requirements.txt` - Python dependencies

## Hazelcast Features Used

- **Distributed Map**: Partitioned, replicated key-value store (AP)
- **Distributed Locks**: Cluster-wide pessimistic locking
- **Atomic Operations**: `replace_if_same()` for optimistic concurrency
- **CP Subsystem**: Raft-based strongly consistent data structures
- **AtomicLong**: Linearizable distributed counter

## Testing Leader Failover

Kill the leader member to test Raft failover:

```bash
# Find the leader in logs
docker logs hazelcast-member-1 | grep LEADER

# Kill it
docker stop hazelcast-member-1

# Watch re-election in remaining members
docker logs -f hazelcast-member-2
```

The counter should continue working seamlessly!

## References

- [Hazelcast Documentation](https://docs.hazelcast.com/)
- [CP Subsystem](https://docs.hazelcast.com/hazelcast/latest/cp-subsystem/cp-subsystem)
- [Raft Consensus Algorithm](https://raft.github.io/)
