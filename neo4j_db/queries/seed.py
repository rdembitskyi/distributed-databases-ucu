from client.connect import get_driver, log


def seed(driver):
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")
        log.info("Cleared existing data")

        # Create items
        items = [
            {"name": "Football Boots", "price": 120.0},
            {"name": "Jersey", "price": 85.0},
            {"name": "Shin Guards", "price": 25.0},
            {"name": "Football", "price": 45.0},
            {"name": "Goalkeeper Gloves", "price": 65.0},
            {"name": "Training Cones", "price": 15.0},
            {"name": "Water Bottle", "price": 10.0},
        ]
        for item in items:
            s.run(
                "CREATE (:Item {name: $name, price: $price})",
                name=item["name"], price=item["price"],
            )
        log.info("Created %d items", len(items))

        # Create customers with orders
        customers = [
            {
                "name": "Alessandro Del Piero",
                "email": "delpiero@example.com",
                "items": [
                    {"name": "Football Boots", "quantity": 1},
                    {"name": "Jersey", "quantity": 2},
                    {"name": "Football", "quantity": 1},
                ],
            },
            {
                "name": "Francesco Totti",
                "email": "totti@example.com",
                "items": [
                    {"name": "Jersey", "quantity": 1},
                    {"name": "Shin Guards", "quantity": 2},
                    {"name": "Water Bottle", "quantity": 3},
                ],
            },
            {
                "name": "Andrea Pirlo",
                "email": "pirlo@example.com",
                "items": [
                    {"name": "Football Boots", "quantity": 1},
                    {"name": "Goalkeeper Gloves", "quantity": 1},
                    {"name": "Training Cones", "quantity": 5},
                ],
            },
            {
                "name": "Paolo Maldini",
                "email": "maldini@example.com",
                "items": [
                    {"name": "Shin Guards", "quantity": 3},
                    {"name": "Jersey", "quantity": 1},
                    {"name": "Football Boots", "quantity": 1},
                ],
            },
            {
                "name": "Roberto Baggio",
                "email": "baggio@example.com",
                "items": [
                    {"name": "Football", "quantity": 2},
                    {"name": "Training Cones", "quantity": 10},
                    {"name": "Water Bottle", "quantity": 5},
                ],
            },
        ]

        for customer in customers:
            s.run(
                """
                CREATE (c:Customer {name: $name, email: $email})
                CREATE (o:Order {id: randomUUID(), created_at: datetime()})
                MERGE (c)-[:PLACED]->(o)
                WITH o
                UNWIND $items AS item
                MATCH (i:Item {name: item.name})
                CREATE (o)-[:CONTAINS {quantity: item.quantity}]->(i)
                """,
                name=customer["name"],
                email=customer["email"],
                items=customer["items"],
            )
        log.info("Created %d customers with orders", len(customers))

        # Add some VIEWED relationships (customers browsed items they didn't buy)
        views = [
            ("Alessandro Del Piero", "Goalkeeper Gloves"),
            ("Francesco Totti", "Football Boots"),
            ("Andrea Pirlo", "Water Bottle"),
            ("Paolo Maldini", "Football"),
            ("Roberto Baggio", "Jersey"),
        ]
        for customer_name, item_name in views:
            s.run(
                """
                MATCH (c:Customer {name: $customer}), (i:Item {name: $item})
                MERGE (c)-[:VIEWED]->(i)
                """,
                customer=customer_name, item=item_name,
            )
        log.info("Added VIEWED relationships")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    d = get_driver()
    seed(d)
    d.close()