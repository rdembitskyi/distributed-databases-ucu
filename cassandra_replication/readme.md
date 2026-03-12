# Cassandra Replication Testing

## 1. Start the cluster

```bash
# Create network and volumes
docker compose up --no-start

# Start node 1 and wait for it to be healthy
docker compose start cassandra-node-1
echo "Waiting for node 1..." && until docker exec cassandra-node-1 nodetool status 2>/dev/null | grep -q "^UN"; do sleep 10; done && echo "Node 1 ready"

# Start node 2 and wait for it to join the ring
docker compose start cassandra-node-2
echo "Waiting for node 2..." && until docker exec cassandra-node-1 nodetool status 2>/dev/null | grep -c "^UN" | grep -q "2"; do sleep 10; done && echo "Node 2 ready"

# Start node 3 and wait for it to join
docker compose start cassandra-node-3
echo "Waiting for node 3..." && until docker exec cassandra-node-1 nodetool status 2>/dev/null | grep -c "^UN" | grep -q "3"; do sleep 10; done && echo "Node 3 ready"
```

## Project structure

- `scripts/data/` — scripts to create keyspaces and tables (`create_keyspaces.py`, `create_tables.py`). Run these first after the cluster is up.
- `scripts/test_consistency.py` — tests read/write at different consistency levels across keyspaces with RF=1, RF=2, RF=3.
- `scripts/test_conflict.py` — writes conflicting data to isolated nodes, then reads after reconnect to observe last-write-wins resolution.
- `scripts/test_lwt.py` — tests lightweight transactions (IF NOT EXISTS, IF condition) on connected and partitioned clusters.

## 2. Check cluster status per keyspace

```bash
for ks in test_keyspace_1 test_keyspace_2 test_keyspace_3; do
  echo "=== $ks ==="
  docker exec cassandra-node-1 nodetool status $ks
  echo ""
done
```

## 3. Install iptables inside containers

Needed to simulate network partitions. Containers must have `cap_add: [NET_ADMIN]` in docker-compose.

```bash
docker exec cassandra-node-1 bash -c "apt-get update && apt-get install -y iptables"
docker exec cassandra-node-2 bash -c "apt-get update && apt-get install -y iptables"
docker exec cassandra-node-3 bash -c "apt-get update && apt-get install -y iptables"
```

## 4. Get container IPs

```bash
docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' cassandra-node-1 cassandra-node-2 cassandra-node-3
```

## 5. Simulate network partition (block inter-node traffic)

Each node drops incoming packets from the other two nodes using iptables.
Host connectivity (localhost port mappings) is preserved — only container-to-container traffic is blocked.

```bash
# Node-1: block node-2 and node-3
docker exec cassandra-node-1 iptables -A INPUT -s 172.18.0.3 -j DROP
docker exec cassandra-node-1 iptables -A INPUT -s 172.18.0.4 -j DROP

# Node-2: block node-1 and node-3
docker exec cassandra-node-2 iptables -A INPUT -s 172.18.0.2 -j DROP
docker exec cassandra-node-2 iptables -A INPUT -s 172.18.0.4 -j DROP

# Node-3: block node-1 and node-2
docker exec cassandra-node-3 iptables -A INPUT -s 172.18.0.2 -j DROP
docker exec cassandra-node-3 iptables -A INPUT -s 172.18.0.3 -j DROP
```

## 6. Restore connectivity

Flush all iptables rules to reconnect the nodes.

```bash
docker exec cassandra-node-1 iptables -F
docker exec cassandra-node-2 iptables -F
docker exec cassandra-node-3 iptables -F
```