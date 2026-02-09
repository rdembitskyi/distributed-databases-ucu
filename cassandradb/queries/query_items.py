from cassandra.cluster import Cluster


def describe_tables():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    result = session.execute("DESCRIBE TABLE items")
    print("=== ITEMS TABLE ===")
    for row in result:
        print(row.create_statement)

    print()

    result = session.execute("DESCRIBE TABLE orders")
    print("=== ORDERS TABLE ===")
    for row in result:
        print(row.create_statement)

    cluster.shutdown()


def items_by_category_sorted_by_price(category):
    """All items in a category, sorted by price (ASC by clustering order)."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE category = %s ORDER BY price ASC",
        (category,),
    )

    print(f"=== Items in '{category}' sorted by price ===")
    for row in rows:
        print(f"  {row.name} | {row.price} | {row.producer} | {row.properties}")

    cluster.shutdown()


def items_by_category_and_name(category, name):
    """Items in a category filtered by name."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE category = %s AND name = %s",
        (category, name),
    )

    print(f"=== Items in '{category}' with name '{name}' ===")
    for row in rows:
        print(f"  {row.name} | {row.price} | {row.producer} | {row.properties}")

    cluster.shutdown()


def items_by_category_and_price_range(category, min_price, max_price):
    """Items in a category within a price range."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE category = %s AND price >= %s AND price <= %s",
        (category, min_price, max_price),
    )

    print(f"=== Items in '{category}' with price {min_price}-{max_price} ===")
    for row in rows:
        print(f"  {row.name} | {row.price} | {row.producer} | {row.properties}")

    cluster.shutdown()


def items_by_category_price_and_producer(category, price, producer):
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE category = %s AND price = %s AND producer = %s",
        (category, price, producer),
    )

    for row in rows:
        print(f"  {row.name} | {row.price} | {row.producer} | {row.properties}")

    cluster.shutdown()


def items_by_property_key(key):
    """Items that have a certain property key (e.g. 'color')."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE properties CONTAINS KEY %s",
        (key,),
    )

    print(f"=== Items with property '{key}' ===")
    for row in rows:
        print(f"  {row.name} | {row.category} | {row.properties}")

    cluster.shutdown()


def items_by_property_key_and_value(key, value):
    """Items with a specific property key-value pair."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM items WHERE properties[%s] = %s",
        (key, value),
    )

    print(f"=== Items with property '{key}' = '{value}' ===")
    for row in rows:
        print(f"  {row.name} | {row.category} | {row.properties}")

    cluster.shutdown()


if __name__ == "__main__":
    # 1 - describe tables
    describe_tables()

    # 2 - items by category sorted by price
    items_by_category_sorted_by_price("electronics")

    # 3 - items by category and name
    items_by_category_and_name("electronics", "Laptop Pro 15")

    # 4 - items by category and price range
    items_by_category_and_price_range("electronics", 20, 100)

    # 5 - items by category, price and producer
    items_by_category_price_and_producer("electronics", 29.99, "LogiTech")

    # 6 - items that have property 'color'
    items_by_property_key("color")

    # 7 - items where color = 'red'
    items_by_property_key_and_value("color", "red")
