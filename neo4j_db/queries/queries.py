from client.connect import get_driver, log


def find_items_by_order(driver, order_id):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (o:Order {id: $order_id})-[r:CONTAINS]->(i:Item)
            RETURN i.name AS name, i.price AS price, r.quantity AS quantity
            """,
            order_id=order_id,
        )
        return [record.data() for record in result]


def calculate_order_total(driver, order_id):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (o:Order {id: $order_id})-[r:CONTAINS]->(i:Item)
            RETURN sum(i.price * r.quantity) AS total
            """,
            order_id=order_id,
        )
        record = result.single()
        return record["total"] if record else 0


def find_orders_by_customer(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:Customer {name: $name})-[:PLACED]->(o:Order)
            RETURN o.id AS id, o.created_at AS created_at
            """,
            name=customer_name,
        )
        return [record.data() for record in result]


def find_items_by_customer(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:Customer {name: $name})-[:PLACED]->(o:Order)-[r:CONTAINS]->(i:Item)
            RETURN i.name AS name, i.price AS price, r.quantity AS quantity, o.id AS order_id
            """,
            name=customer_name,
        )
        return [record.data() for record in result]


def count_items_by_customer(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:Customer {name: $name})-[:PLACED]->(:Order)-[r:CONTAINS]->(:Item)
            RETURN sum(r.quantity) AS total_items
            """,
            name=customer_name,
        )
        record = result.single()
        return record["total_items"] if record else 0


def calculate_customer_total_spent(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (:Customer {name: $name})-[:PLACED]->(:Order)-[r:CONTAINS]->(i:Item)
            RETURN sum(i.price * r.quantity) AS total_spent
            """,
            name=customer_name,
        )
        record = result.single()
        return record["total_spent"] if record else 0


def find_viewed_items_by_customer(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (:Customer {name: $name})-[:VIEWED]->(i:Item)
            RETURN i.name AS name, i.price AS price
            """,
            name=customer_name,
        )
        return [record.data() for record in result]


def items_purchase_count(driver):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (:Order)-[r:CONTAINS]->(i:Item)
            RETURN i.name AS name, sum(r.quantity) AS total_purchased
            ORDER BY total_purchased DESC
            """,
        )
        return [record.data() for record in result]


def find_items_bought_together(driver, item_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (target:Item {name: $name})<-[:CONTAINS]-(:Order)-[:CONTAINS]->(other:Item)
            WHERE other.name <> $name
            RETURN DISTINCT other.name AS name, other.price AS price
            """,
            name=item_name,
        )
        return [record.data() for record in result]



def find_customer_bought_item(driver, item_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (target:Item {name: $name})<-[:CONTAINS]-(:Order)<-[:PLACED]-(c:Customer)
            RETURN c.name AS name
            """,
            name=item_name,
        )
        return [record.data() for record in result]


def find_viewed_but_not_bought(driver, customer_name):
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:Customer {name: $name})-[:VIEWED]->(i:Item)
            WHERE NOT (c)-[:PLACED]->(:Order)-[:CONTAINS]->(i)
            RETURN i.name AS name, i.price AS price
            """,
            name=customer_name,
        )
        return [record.data() for record in result]


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    d = get_driver()

    # Get first order id to test
    with d.session() as s:
        order = s.run("MATCH (o:Order) RETURN o.id AS id LIMIT 1").single()
        if order:
            oid = order["id"]
            log.info("Items in order %s:", oid)
            for item in find_items_by_order(d, oid):
                log.info("  %s x%d — $%.2f", item["name"], item["quantity"], item["price"])
            total = calculate_order_total(d, oid)
            log.info("Order total: $%.2f", total)

    # Test find_orders_by_customer
    customer_name = "Alessandro Del Piero"
    orders = find_orders_by_customer(d, customer_name)
    log.info("Orders for %s:", customer_name)
    for o in orders:
        log.info("  Order %s, created at %s", o["id"], o["created_at"])

    # Test find_items_by_customer
    items = find_items_by_customer(d, customer_name)
    log.info("Items bought by %s:", customer_name)
    for item in items:
        log.info("  %s x%d — $%.2f (order %s)", item["name"], item["quantity"], item["price"], item["order_id"])

    # Test count_items_by_customer
    total_items = count_items_by_customer(d, customer_name)
    log.info("Total items bought by %s: %d", customer_name, total_items)

    # Test calculate_customer_total_spent
    total_spent = calculate_customer_total_spent(d, customer_name)
    log.info("Total spent by %s: $%.2f", customer_name, total_spent)

    # Test items_purchase_count
    counts = items_purchase_count(d)
    log.info("Items by purchase count:")
    for c in counts:
        log.info("  %s — %d", c["name"], c["total_purchased"])

    # Test find_viewed_items_by_customer
    viewed = find_viewed_items_by_customer(d, customer_name)
    log.info("Items viewed by %s:", customer_name)
    for v in viewed:
        log.info("  %s — $%.2f", v["name"], v["price"])

    # Test find_items_bought_together
    test_item = "Football Boots"
    together = find_items_bought_together(d, test_item)
    log.info("Items bought together with %s:", test_item)
    for t in together:
        log.info("  %s — $%.2f", t["name"], t["price"])

    # Test find_customer_bought_item
    buyers = find_customer_bought_item(d, test_item)
    log.info("Customers who bought %s:", test_item)
    for b in buyers:
        log.info("  %s", b["name"])

    # Test find_viewed_but_not_bought
    viewed_not_bought = find_viewed_but_not_bought(d, customer_name)
    log.info("Items viewed but not bought by %s:", customer_name)
    for v in viewed_not_bought:
        log.info("  %s — $%.2f", v["name"], v["price"])

    d.close()