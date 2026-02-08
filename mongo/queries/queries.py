import json
import logging

from client.connect import get_client

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ITEMS = [
    # Phones
    {"category": "Phone", "model": "iPhone 15 Pro", "producer": "Apple", "price": 1199},
    {"category": "Phone", "model": "iPhone 14", "producer": "Apple", "price": 799},
    {"category": "Phone", "model": "Galaxy S23", "producer": "Samsung", "price": 899},
    {"category": "Phone", "model": "Pixel 8 Pro", "producer": "Google", "price": 999},
    {"category": "Phone", "model": "OnePlus 11", "producer": "OnePlus", "price": 699},
    # TVs
    {"category": "TV", "model": 'OLED C3 65"', "producer": "LG", "price": 1799},
    {"category": "TV", "model": 'QN90C 55"', "producer": "Samsung", "price": 1499},
    {"category": "TV", "model": "Bravia XR A95K", "producer": "Sony", "price": 2499},
    {"category": "TV", "model": 'Fire TV 50"', "producer": "Amazon", "price": 449},
    {"category": "TV", "model": 'U8K 65"', "producer": "Hisense", "price": 899},
    # Fridges
    {
        "category": "Fridge",
        "model": "French Door RF29",
        "producer": "Samsung",
        "price": 2199,
    },
    {
        "category": "Fridge",
        "model": "InstaView LRFXS2503S",
        "producer": "LG",
        "price": 1899,
    },
    {
        "category": "Fridge",
        "model": "Profile PVD28BYNFS",
        "producer": "GE",
        "price": 2499,
    },
    {
        "category": "Fridge",
        "model": "WRX735SDHZ",
        "producer": "Whirlpool",
        "price": 1599,
    },
    # Laptops
    {
        "category": "Laptop",
        "model": 'MacBook Pro 16"',
        "producer": "Apple",
        "price": 2499,
    },
    {
        "category": "Laptop",
        "model": "ThinkPad X1 Carbon",
        "producer": "Lenovo",
        "price": 1449,
    },
    {"category": "Laptop", "model": "XPS 15", "producer": "Dell", "price": 1299},
    {"category": "Laptop", "model": "Spectre x360", "producer": "HP", "price": 1399},
    # Headphones
    {
        "category": "Headphones",
        "model": "AirPods Pro 2",
        "producer": "Apple",
        "price": 249,
    },
    {"category": "Headphones", "model": "WH-1000XM5", "producer": "Sony", "price": 349},
]


def insert_items():
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    if collection.count_documents({}) > 0:
        log.info("Collection 'items' already has data, skipping seed")
        return

    result = collection.insert_many(ITEMS)
    log.info("Inserted %d items", len(result.inserted_ids))


def get_all_items():
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    items = list(collection.find({}, {"_id": 0}))
    log.info("Found %d items", len(items))
    return items


def count_items_by_category():
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    results = list(collection.aggregate(pipeline))
    log.info("Found %d categories", len(results))
    return results


def count_categories():
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    count = len(collection.distinct("category"))
    log.info("Found %d distinct categories", count)
    return count


def get_distinct_producers():
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    producers = collection.distinct("producer")
    log.info("Found %d distinct producers", len(producers))
    return producers


def find_by_category_and_price(category, min_price, max_price):
    """$and — filter by category and price range"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    query = {
        "$and": [
            {"category": category},
            {"price": {"$gte": min_price, "$lte": max_price}},
        ]
    }
    items = list(collection.find(query, {"_id": 0}))
    log.info(
        "Found %d items (category=%s, price %d-%d)",
        len(items),
        category,
        min_price,
        max_price,
    )
    return items


def find_by_model_or(model1, model2):
    """$or — one model or another"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    query = {
        "$or": [
            {"model": model1},
            {"model": model2},
        ]
    }
    items = list(collection.find(query, {"_id": 0}))
    log.info("Found %d items (model=%s or %s)", len(items), model1, model2)
    return items


def find_by_producers(producers):
    """$in — producers from a given list"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    query = {"producer": {"$in": producers}}
    items = list(collection.find(query, {"_id": 0}))
    log.info("Found %d items (producers=%s)", len(items), producers)
    return items


def update_iphone_prices(price_increase):
    """Update existing field: increase price for Apple phones"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    result = collection.update_many(
        {"category": "Phone", "producer": "Apple"},
        {"$inc": {"price": price_increase}},
    )
    log.info(
        "Matched %d, modified %d (Apple phone prices +%d)",
        result.matched_count,
        result.modified_count,
        price_increase,
    )
    return result


def add_warranty_to_items(min_price, warranty_years):
    """Add new properties: warranty and in_stock to all items above min_price"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    result = collection.update_many(
        {"price": {"$gte": min_price}},
        {"$set": {"warranty_years": warranty_years, "in_stock": True}},
    )
    log.info(
        "Matched %d, modified %d (added warranty=%d, in_stock=True where price >= %d)",
        result.matched_count,
        result.modified_count,
        warranty_years,
        min_price,
    )
    return result


def find_items_with_field(field):
    """$exists — find items where a specific field is present"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    query = {field: {"$exists": True}}
    items = list(collection.find(query, {"_id": 0}))
    log.info("Found %d items with field '%s'", len(items), field)
    return items


def increase_price_for_warranty_items(price_increase):
    """Increase price for all items that have the warranty_years field"""
    client = get_client()
    db = client["shop"]
    collection = db["items"]

    result = collection.update_many(
        {"warranty_years": {"$exists": True}},
        {"$inc": {"price": price_increase}},
    )
    log.info(
        "Matched %d, modified %d (warranty items prices +%d)",
        result.matched_count,
        result.modified_count,
        price_increase,
    )
    return result


if __name__ == "__main__":
    # insert_items()
    items = get_all_items()
    print(json.dumps(items, indent=2))

    print("\nItems per category:")
    for cat in count_items_by_category():
        print(f"  {cat['_id']}: {cat['count']}")

    print(f"\nTotal categories: {count_categories()}")

    print("\nDistinct producers:")
    for producer in get_distinct_producers():
        print(f"  {producer}")

    # $and: phones with price between 800 and 1000
    print("\n$and — Phones with price 800-1000:")
    print(json.dumps(find_by_category_and_price("Phone", 800, 1000), indent=2))

    # $or: one model or another
    print("\n$or — iPhone 15 Pro or Galaxy S23:")
    print(json.dumps(find_by_model_or("iPhone 15 Pro", "Galaxy S23"), indent=2))

    # $in: items from specific producers
    print("\n$in — Items by Apple, Sony, LG:")
    print(json.dumps(find_by_producers(["Apple", "Sony", "LG"]), indent=2))

    # updateMany: increase Apple phone prices by 50
    print("\nupdateMany — Apple phone prices +50:")
    update_iphone_prices(50)
    print(json.dumps(find_by_producers(["Apple"]), indent=2))

    # updateMany: add warranty_years and in_stock to all items >= 1500
    print("\nupdateMany — Add warranty & in_stock to items >= $1500:")
    add_warranty_to_items(1500, 3)
    print(
        json.dumps(
            list(
                get_client()["shop"]["items"].find(
                    {"price": {"$gte": 1500}}, {"_id": 0}
                )
            ),
            indent=2,
        )
    )

    # $exists: find items that have the warranty_years field
    print("\n$exists — Items with warranty:")
    print(json.dumps(find_items_with_field("warranty_years"), indent=2))

    # increase price by 100 for items with warranty
    print("\nupdateMany — Warranty items prices +100:")
    increase_price_for_warranty_items(100)
    print(json.dumps(find_items_with_field("warranty_years"), indent=2))
