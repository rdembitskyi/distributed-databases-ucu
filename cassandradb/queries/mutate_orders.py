import uuid
from datetime import datetime

from cassandra.cluster import Cluster


def add_items_to_order(customer_name, order_date, order_id, item_names):
    """Add items to an order and update total price."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    new_ids = set()
    added_price = 0
    for name in item_names:
        item_row = session.execute(
            "SELECT id, price FROM items WHERE name = %s", (name,)
        ).one()
        if not item_row:
            print(f"Item '{name}' not found, skipping")
            continue
        new_ids.add(item_row.id)
        added_price += float(item_row.price)

    current = session.execute(
        "SELECT total_price FROM orders WHERE customer_name = %s AND order_date = %s AND id = %s",
        (customer_name, order_date, order_id),
    ).one()
    new_price = float(current.total_price) + added_price

    session.execute(
        "UPDATE orders SET item_ids = item_ids + %s, total_price = %s "
        "WHERE customer_name = %s AND order_date = %s AND id = %s",
        (new_ids, new_price, customer_name, order_date, order_id),
    )

    print(
        f"Added {len(new_ids)} items to order {order_id}, price increased by {added_price}"
    )
    cluster.shutdown()


def remove_items_from_order(customer_name, order_date, order_id, item_names):
    """Remove items from an order and update total price."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    remove_ids = set()
    removed_price = 0
    for name in item_names:
        item_row = session.execute(
            "SELECT id, price FROM items WHERE name = %s", (name,)
        ).one()
        if not item_row:
            print(f"Item '{name}' not found, skipping")
            continue
        remove_ids.add(item_row.id)
        removed_price += float(item_row.price)

    current = session.execute(
        "SELECT total_price FROM orders WHERE customer_name = %s AND order_date = %s AND id = %s",
        (customer_name, order_date, order_id),
    ).one()
    new_price = float(current.total_price) - removed_price

    session.execute(
        "UPDATE orders SET item_ids = item_ids - %s, total_price = %s "
        "WHERE customer_name = %s AND order_date = %s AND id = %s",
        (remove_ids, new_price, customer_name, order_date, order_id),
    )

    print(
        f"Removed {len(remove_ids)} items from order {order_id}, price decreased by {removed_price}"
    )
    cluster.shutdown()


def print_order(customer_name):
    """Print all orders for a customer."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM orders WHERE customer_name = %s", (customer_name,)
    )
    for row in rows:
        print(
            f"  {row.customer_name} | {row.order_date} | {row.item_ids} | {row.total_price}"
        )

    cluster.shutdown()


def get_first_order(customer_name):
    """Get the first order for a customer (most recent by date)."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    row = session.execute(
        "SELECT * FROM orders WHERE customer_name = %s LIMIT 1", (customer_name,)
    ).one()

    cluster.shutdown()
    return row


def create_order_with_ttl(customer_name, item_names, ttl_seconds):
    """Create an order with a TTL — it will be automatically deleted after ttl_seconds."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    item_ids = set()
    total_price = 0
    for name in item_names:
        item_row = session.execute(
            "SELECT id, price FROM items WHERE name = %s", (name,)
        ).one()
        if not item_row:
            print(f"Item '{name}' not found, skipping")
            continue
        item_ids.add(item_row.id)
        total_price += float(item_row.price)

    order_id = uuid.uuid4()
    session.execute(
        "INSERT INTO orders (id, customer_name, order_date, item_ids, total_price, status) "
        "VALUES (%s, %s, %s, %s, %s, %s) USING TTL %s",
        (
            order_id,
            customer_name,
            datetime.now(),
            item_ids,
            total_price,
            "pending",
            ttl_seconds,
        ),
    )

    print(
        f"Created order {order_id} for '{customer_name}' with TTL={ttl_seconds}s (total: {total_price})"
    )
    cluster.shutdown()


if __name__ == "__main__":
    customer = "Alice Johnson"
    order = get_first_order(customer)

    print(f"=== Before adding item ===")
    print_order(customer)

    # Add an item
    add_items_to_order(customer, order.order_date, order.id, ["Yoga Mat"])

    print(f"\n=== After adding 'Yoga Mat' ===")
    print_order(customer)

    # Remove the item
    remove_items_from_order(customer, order.order_date, order.id, ["Yoga Mat"])

    print(f"\n=== After removing 'Yoga Mat' ===")
    print_order(customer)

    # Create an order with TTL of 30 seconds
    print(f"\n=== Creating order with TTL=30s ===")
    create_order_with_ttl("Alice Johnson", ["Coffee Maker", "Yoga Mat"], 30)
    print_order("Alice Johnson")
