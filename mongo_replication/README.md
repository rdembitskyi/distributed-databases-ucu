# MongoDB PSS Replication

3-node Primary-Secondary-Secondary replica set using Docker Compose.

## Setup

1. Add Docker hostnames to `/etc/hosts`:
   ```bash
   sudo sh -c 'echo "127.0.0.1 mongo1 mongo2 mongo3" >> /etc/hosts'
   ```

2. Start the cluster:
   ```bash
   docker compose up -d
   ```

3. Verify replica set status:
   ```bash
   docker exec mongo1 mongosh --port 27017 --eval "rs.status()"
   ```

## Nodes

| Node   | Host        | Port  | Role      |
|--------|-------------|-------|-----------|
| mongo1 | mongo1:27017 | 27017 | Primary   |
| mongo2 | mongo2:27018 | 27018 | Secondary |
| mongo3 | mongo3:27019 | 27019 | Secondary |

## Testing failover

```bash
# Stop a node
docker compose stop mongo2

# Start it back
docker compose start mongo2

# Pause/unpause (freezes process, keeps container)
docker compose pause mongo2
docker compose unpause mongo2
```

## Connection URI

```
mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=rs_test
```
