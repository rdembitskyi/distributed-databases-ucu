from cassandra.cluster import Cluster


def update_item_property(category, price, producer, item_id, key, new_value):
    """Update a specific property value for an item."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    session.execute(
        "UPDATE items SET properties[%s] = %s WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (key, new_value, category, price, producer, item_id),
    )

    print(f"Updated property '{key}' to '{new_value}'")

    row = session.execute(
        "SELECT * FROM items WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (category, price, producer, item_id),
    ).one()

    print(f"  {row.name} | {row.properties}")

    cluster.shutdown()


def add_item_properties(category, price, producer, item_id, new_properties):
    """Add new properties to an item's properties map."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    session.execute(
        "UPDATE items SET properties = properties + %s WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (new_properties, category, price, producer, item_id),
    )

    print(f"Added properties: {new_properties}")

    row = session.execute(
        "SELECT * FROM items WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (category, price, producer, item_id),
    ).one()

    print(f"  {row.name} | {row.properties}")

    cluster.shutdown()


def delete_item_property(category, price, producer, item_id, key):
    """Delete a specific property from an item's properties map."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    session.execute(
        "DELETE properties[%s] FROM items WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (key, category, price, producer, item_id),
    )

    print(f"Deleted property '{key}'")

    row = session.execute(
        "SELECT * FROM items WHERE category = %s AND price = %s AND producer = %s AND id = %s",
        (category, price, producer, item_id),
    ).one()

    print(f"  {row.name} | {row.properties}")

    cluster.shutdown()


if __name__ == "__main__":
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    row = session.execute(
        "SELECT * FROM items WHERE category = 'electronics' LIMIT 1"
    ).one()

    cluster.shutdown()

    if row:
        print(f"Before: {row.name} | {row.properties}")
        # update existing property
        update_item_property(
            row.category,
            row.price,
            row.producer,
            row.id,
            "color",
            "midnight-black",
        )
        print()
        # add new properties
        add_item_properties(
            row.category,
            row.price,
            row.producer,
            row.id,
            {"warranty": "2 years", "weight": "350g"},
        )
        print()
        # delete a property
        delete_item_property(
            row.category,
            row.price,
            row.producer,
            row.id,
            "weight",
        )
