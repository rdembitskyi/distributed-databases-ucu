import logging
from datetime import datetime

from pymongo.errors import CollectionInvalid
from utils import JSONEncoder
from client.connect import get_client

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_capped_reviews():
    """Create a capped collection for reviews (max 5 documents)"""
    client = get_client()
    db = client["shop"]

    try:
        db.create_collection("reviews", capped=True, size=4096, max=5)
    except CollectionInvalid:
        log.info("Collection 'reviews' already exists")


def add_review(author, rating, text, item_model):
    """Add a review to the capped collection with a reference to an item"""
    client = get_client()
    db = client["shop"]

    item = db["items"].find_one({"model": item_model}, {"_id": 1})
    if not item:
        log.info("Item '%s' not found", item_model)
        return

    review = {
        "author": author,
        "rating": rating,
        "text": text,
        "item_id": item["_id"],
        "date": datetime.now(),
    }
    db["reviews"].insert_one(review)
    log.info("Added review by %s for '%s' (rating=%d)", author, item_model, rating)


def get_all_reviews():
    """Get all reviews"""
    client = get_client()
    db = client["shop"]
    collection = db["reviews"]

    results = list(collection.find({}, {"_id": 0}))
    log.info("Found %d reviews", len(results))
    return results


if __name__ == "__main__":
    create_capped_reviews()

    # Insert 7 reviews — only the last 5 should remain
    reviews = [
        ("Paolo Maldini", 5, "Great shop, fast delivery!"),
        ("Olena Shevchenko", 4, "Good prices, nice selection"),
        ("Dmytro Koval", 3, "Average experience, slow support"),
        ("Zinedine Zidane", 5, "Excellent! Will buy again"),
        ("Kaka Ricardo", 4, "Good quality products"),
        ("Ronaldinho Gaucho", 2, "Delivery was late"),
        ("Cafu Marcos", 5, "Best online shop ever!"),
    ]

    for author, rating, text in reviews:
        add_review(author, rating, text, "iPhone 15 Pro")

    # Only last 5 reviews should be here (first 2 overwritten)
    print("Reviews in capped collection (max 5):")
    print(JSONEncoder(indent=2).encode(get_all_reviews()))
    print(f"\nTotal reviews: {len(get_all_reviews())} (max 5)")
