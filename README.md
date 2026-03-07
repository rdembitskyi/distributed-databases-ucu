# Distributed Databases Course - UCU

A collection of basic store implementations on different storage backends to get familiar with them. Built as part of the Distributed Databases course at Ukrainian Catholic University.

Covered storages: **PostgreSQL, MongoDB, Cassandra, Neo4j, Hazelcast**.

## Projects

### [Web Counter](./web_counter)
Async web counter (FastAPI) that benchmarks different storage backends by measuring RPS. Supports in-memory, disk, PostgreSQL, Hazelcast, MongoDB, Cassandra, and Neo4j.

### [Hazelcast Counter](./hazelcast_counter)
Hazelcast distributed data structures — AtomicLong and distributed map with CP Subsystem.

### [MongoDB](./mongo)
MongoDB queries and operations.

### [Cassandra](./cassandradb)
Cassandra cluster setup and queries.

### [Neo4j](./neo4j_db)
Neo4j graph database queries and operations.

### [Massive Insert](./massive_insert)
Bulk insert benchmarks across different storage backends.
