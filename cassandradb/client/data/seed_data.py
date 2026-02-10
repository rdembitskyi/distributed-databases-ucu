import uuid
from datetime import datetime

from cassandra.cluster import Cluster


def seed_data():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    session.execute("TRUNCATE items")
    session.execute("TRUNCATE orders")

    items = [
        (
            "Laptop Pro 15",
            "electronics",
            1299.99,
            "TechCorp",
            {"screen_size": "15.6 inch", "ram": "16GB", "storage": "512GB SSD"},
        ),
        (
            "Wireless Mouse",
            "electronics",
            29.99,
            "LogiTech",
            {"color": "black", "connectivity": "bluetooth", "battery": "AA"},
        ),
        (
            "Running Shoes",
            "footwear",
            89.99,
            "Nike",
            {"size": "42", "color": "red", "material": "mesh"},
        ),
        (
            "Winter Jacket",
            "clothing",
            149.99,
            "NorthFace",
            {"size": "L", "color": "blue", "waterproof": "yes"},
        ),
        (
            "Coffee Maker",
            "kitchen",
            59.99,
            "Breville",
            {"capacity": "12 cups", "color": "silver", "power": "1000W"},
        ),
        (
            "Yoga Mat",
            "sports",
            24.99,
            "Manduka",
            {"thickness": "6mm", "color": "purple", "material": "TPE"},
        ),
        (
            "Mechanical Keyboard",
            "electronics",
            79.99,
            "Keychron",
            {"switch_type": "brown", "layout": "TKL", "backlight": "RGB"},
        ),
        (
            "Hiking Backpack",
            "sports",
            109.99,
            "Osprey",
            {"capacity": "40L", "color": "green", "waterproof": "yes"},
        ),
    ]

    item_ids = []
    for name, category, price, producer, properties in items:
        item_id = uuid.uuid4()
        item_ids.append(item_id)
        session.execute(
            """
            INSERT INTO items (id, name, category, price, producer, properties)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (item_id, name, category, price, producer, properties),
        )

    print(f"Inserted {len(items)} items")

    orders = [
        ("Alice Johnson", {item_ids[0], item_ids[1]}, 1329.98, "delivered"),
        ("Alice Johnson", {item_ids[6]}, 79.99, "pending"),
        ("Bob Smith", {item_ids[2], item_ids[5]}, 114.98, "shipped"),
        ("Charlie Brown", {item_ids[4], item_ids[3]}, 209.98, "pending"),
        ("Charlie Brown", {item_ids[7], item_ids[6], item_ids[2]}, 279.97, "delivered"),
    ]

    for customer, items_set, total, status in orders:
        session.execute(
            """
            INSERT INTO orders (id, customer_name, order_date, item_ids, total_price, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (uuid.uuid4(), customer, datetime.now(), items_set, total, status),
        )

    print(f"Inserted {len(orders)} orders")

    cluster.shutdown()


if __name__ == "__main__":
    seed_data()
