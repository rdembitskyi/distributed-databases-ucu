from datetime import datetime

from cassandra.cluster import Cluster


def describe_orders():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    result = session.execute("DESCRIBE TABLE orders")
    print("=== ORDERS TABLE ===")
    for row in result:
        print(row.create_statement)

    cluster.shutdown()


def orders_by_customer_sorted_by_date(customer_name):
    """All orders for a customer, sorted by order date (DESC by clustering order)."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT * FROM orders WHERE customer_name = %s ORDER BY order_date DESC",
        (customer_name,),
    )

    print(f"=== Orders for '{customer_name}' sorted by date ===")
    for row in rows:
        print(
            f"  {row.id} | {row.order_date} | {row.item_ids} | {row.total_price} | {row.status}"
        )

    cluster.shutdown()


def orders_by_customer_with_item(customer_name, item_name):
    """Find orders for a customer that contain a specific item (looked up by name)."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    item_rows = session.execute(
        "SELECT id FROM items WHERE name = %s",
        (item_name,),
    )
    item_row = item_rows.one()
    if not item_row:
        print(f"Item '{item_name}' not found")
        cluster.shutdown()
        return

    item_id = item_row.id

    rows = session.execute(
        "SELECT * FROM orders WHERE customer_name = %s AND item_ids CONTAINS %s",
        (customer_name, item_id),
    )

    print(f"=== Orders for '{customer_name}' containing '{item_name}' ===")
    for row in rows:
        print(
            f"  {row.id} | {row.order_date} | {row.item_ids} | {row.total_price} | {row.status}"
        )

    cluster.shutdown()


def orders_by_customer_in_period(customer_name, start_date, end_date):
    """Find orders for a customer within a time period and their count."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    count_rows = session.execute(
        "SELECT COUNT(*) as cnt FROM orders WHERE customer_name = %s AND order_date >= %s AND order_date <= %s",
        (customer_name, start_date, end_date),
    )

    print(
        f"  Total count for {customer_name} from {start_date} to {end_date}: {count_rows.one().cnt} "
    )

    cluster.shutdown()


def max_price_order_per_customer():
    """For each customer, find the order with the maximum total price."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT customer_name, MAX(total_price) as max_price FROM orders GROUP BY customer_name"
    )

    print("=== Max price order per customer ===")
    for row in rows:
        print(f"  {row.customer_name} | max total_price: {row.max_price}")

    cluster.shutdown()


def writetime_of_total_price():
    """For each order, show when total_price was written to the database."""
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    rows = session.execute(
        "SELECT customer_name, id, total_price, WRITETIME(total_price) as wt FROM orders"
    )

    print("=== WRITETIME of total_price for each order ===")
    for row in rows:
        wt = datetime.fromtimestamp(row.wt / 1_000_000)
        print(
            f"  {row.customer_name} | {row.id} | {row.total_price} | writetime: {wt:%Y-%m-%d %H:%M:%S}"
        )

    cluster.shutdown()


if __name__ == "__main__":
    # 1 - describe orders table
    describe_orders()

    # 2 - orders by customer sorted by date
    orders_by_customer_sorted_by_date("Alice Johnson")

    # 3 - orders by customer containing a specific item (by name)
    orders_by_customer_with_item("Alice Johnson", "Laptop Pro 15")

    # 4 - orders by customer in a time period + count
    orders_by_customer_in_period("Alice Johnson", "2025-01-01", "2026-12-31")

    # 5 - max price order per customer
    max_price_order_per_customer()

    # 6 - writetime of total_price for each order
    writetime_of_total_price()
