import logging
from datetime import datetime

from utils import JSONEncoder
from client.connect import get_client

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_item_ids():
    """Get item _id values by model name for use as references"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    items = {item["model"]: item["_id"] for item in collection.find()}
    log.info("Loaded %d item IDs", len(items))
    return items


def create_orders():
    """Create orders with embedded customer and referenced items"""
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    if orders.count_documents({}) > 0:
        log.info("Collection 'orders' already has data, skipping seed")
        return

    item_ids = get_item_ids()

    # iPhone 15 Pro is in both order 1 and order 3 (shared item)
    orders_data = [
        {
            "order_number": 100001,
            "date": datetime(2025, 1, 15),
            "total_sum": 2098,
            "customer": {
                "name": "Andrea",
                "surname": "Pirlo",
                "phones": [9876543, 1234567],
                "address": "PTI, Peremohy 37, Kyiv, UA",
            },
            "payment": {
                "card_owner": "Andrea Pirlo",
                "cardId": 12345678,
            },
            "items_id": [
                item_ids["iPhone 15 Pro"],
                item_ids["Galaxy S23"],
            ],
        },
        {
            "order_number": 100002,
            "date": datetime(2025, 2, 20),
            "total_sum": 4298,
            "customer": {
                "name": "Olena",
                "surname": "Shevchenko",
                "phones": [5551234],
                "address": "Khreshchatyk 10, Kyiv, UA",
            },
            "payment": {
                "card_owner": "Olena Shevchenko",
                "cardId": 87654321,
            },
            "items_id": [
                item_ids['MacBook Pro 16"'],
                item_ids['OLED C3 65"'],
            ],
        },
        {
            "order_number": 100003,
            "date": datetime(2025, 3, 5),
            "total_sum": 1797,
            "customer": {
                "name": "Dmytro",
                "surname": "Koval",
                "phones": [5559876, 5554321],
                "address": "Sadova 25, Lviv, UA",
            },
            "payment": {
                "card_owner": "Dmytro Koval",
                "cardId": 11223344,
            },
            "items_id": [
                item_ids["iPhone 15 Pro"],  # shared with order 1
                item_ids["WH-1000XM5"],
                item_ids["AirPods Pro 2"],
            ],
        },
    ]

    result = orders.insert_many(orders_data)
    log.info("Inserted %d orders", len(result.inserted_ids))


def get_all_orders():
    """Get all orders"""
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    results = list(orders.find({}, {"_id": 0}))
    log.info("Found %d orders", len(results))
    return results


def get_orders_with_items():
    """$lookup — join orders with their referenced items"""
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    pipeline = [
        {
            "$lookup": {
                "from": "items",
                "localField": "items_id",
                "foreignField": "_id",
                "as": "items",
            }
        },
        {"$project": {"_id": 0, "items_id": 0, "items._id": 0}},
    ]
    results = list(orders.aggregate(pipeline))
    log.info("Found %d orders with items", len(results))
    return results


def find_orders_above(min_total):
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    query = {"total_sum": {"$gt": min_total}}
    results = list(orders.find(query, {"_id": 0}))
    log.info("Found %d orders with total_sum > %d", len(results), min_total)
    return results


def find_orders_by_customer(name, surname):
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    query = {"customer.name": name, "customer.surname": surname}
    results = list(orders.find(query, {"_id": 0}))
    log.info("Found %d orders by %s %s", len(results), name, surname)
    return results


def find_orders_by_item(model_name):
    """Find all orders containing a specific item (by ObjectId)"""
    client = get_client()
    db = client["shop"]

    item = db["items"].find_one({"model": model_name}, {"_id": 1})
    if not item:
        log.info("Item '%s' not found", model_name)
        return []

    item_id = item["_id"]
    log.info("Looking for orders with item '%s' (id=%s)", model_name, item_id)

    results = list(db["orders"].find({"items_id": item_id}, {"_id": 0}))
    log.info("Found %d orders with item '%s'", len(results), model_name)
    return results


def add_item_to_orders(target_model, new_model, price_increase):
    """Add a new item to all orders containing target_model and increase total_sum"""
    client = get_client()
    db = client["shop"]

    target = db["items"].find_one({"model": target_model}, {"_id": 1})
    new_item = db["items"].find_one({"model": new_model}, {"_id": 1})
    if not target or not new_item:
        log.info("Item not found: target=%s, new=%s", target_model, new_model)
        return

    result = db["orders"].update_many(
        {"items_id": target["_id"]},
        {
            "$push": {"items_id": new_item["_id"]},
            "$inc": {"total_sum": price_increase},
        },
    )
    log.info(
        "Matched %d, modified %d (added '%s', total_sum +%d to orders with '%s')",
        result.matched_count,
        result.modified_count,
        new_model,
        price_increase,
        target_model,
    )
    return result


def get_customer_info_for_expensive_orders(min_total):
    """Get only customer and payment info for orders above min_total"""
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    query = {"total_sum": {"$gt": min_total}}
    projection = {"_id": 0, "customer": 1, "payment.cardId": 1}
    results = list(orders.find(query, projection))
    log.info("Found %d orders with total_sum > %d", len(results), min_total)
    return results


def remove_item_from_orders_in_period(model_name, date_from, date_to):
    """$pull — remove an item from orders made within a date range"""
    client = get_client()
    db = client["shop"]

    item = db["items"].find_one({"model": model_name}, {"_id": 1})
    if not item:
        log.info("Item '%s' not found", model_name)
        return

    result = db["orders"].update_many(
        {"date": {"$gte": date_from, "$lte": date_to}},
        {"$pull": {"items_id": item["_id"]}},
    )
    return result


def rename_customer(old_name, old_surname, new_name, new_surname):
    """Rename a customer across all their orders"""
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    result = orders.update_many(
        {"customer.name": old_name, "customer.surname": old_surname},
        {
            "$set": {
                "customer.name": new_name,
                "customer.surname": new_surname,
                "payment.card_owner": f"{new_name} {new_surname}",
            }
        },
    )
    return result


def get_order_details(order_number):
    client = get_client()
    db = client["shop"]
    orders = db["orders"]

    pipeline = [
        {"$match": {"order_number": order_number}},
        {
            "$lookup": {
                "from": "items",
                "localField": "items_id",
                "foreignField": "_id",
                "as": "items",
            }
        },
        {
            "$project": {
                "_id": 0,
                "order_number": 1,
                "customer.surname": 1,
                "items.model": 1,
                "items.price": 1,
            }
        },
    ]
    results = list(orders.aggregate(pipeline))
    return results[0] if results else None


if __name__ == "__main__":
    create_orders()

    print("All orders:")
    print(JSONEncoder(indent=2).encode(get_all_orders()))

    print("\nOrders with resolved items ($lookup):")
    print(JSONEncoder(indent=2).encode(get_orders_with_items()))

    # Orders with total_sum > 2000
    print("\nOrders with total > 2000:")
    print(JSONEncoder(indent=2).encode(find_orders_above(2000)))

    # Find orders by a specific customer
    print("\nOrders by Andrea Pirlo:")
    print(JSONEncoder(indent=2).encode(find_orders_by_customer("Andrea", "Pirlo")))

    # Find orders containing iPhone 15 Pro (shared between order 1 and 3)
    print("\nOrders with iPhone 15 Pro:")
    print(JSONEncoder(indent=2).encode(find_orders_by_item("iPhone 15 Pro")))

    # Add Pixel 8 Pro to all orders that have iPhone 15 Pro, increase total by 999
    print("\nupdateMany — Add Pixel 8 Pro to orders with iPhone 15 Pro (+999):")
    add_item_to_orders("iPhone 15 Pro", "Pixel 8 Pro", 999)
    print(JSONEncoder(indent=2).encode(find_orders_by_item("iPhone 15 Pro")))

    # Customer + cardId for orders > 2000
    print("\nCustomer info for orders > 2000:")
    print(JSONEncoder(indent=2).encode(get_customer_info_for_expensive_orders(2000)))

    # Remove Galaxy S23 from orders made in Jan-Feb 2025
    print("\n$pull — Remove Galaxy S23 from orders in Jan-Feb 2025:")
    remove_item_from_orders_in_period(
        "Galaxy S23", datetime(2025, 1, 1), datetime(2025, 2, 28)
    )
    print(JSONEncoder(indent=2).encode(get_orders_with_items()))

    # Rename customer Andrea Pirlo -> Paolo Maldini in all orders
    print("\nupdateMany — Rename Andrea Pirlo -> Paolo Maldini:")
    rename_customer("Andrea", "Pirlo", "Paolo", "Maldini")
    print(JSONEncoder(indent=2).encode(get_all_orders()))

    # Get order details: customer surname + item names and prices
    print("\nOrder 100001 details (customer + items join):")
    print(JSONEncoder(indent=2).encode(get_order_details(100001)))
