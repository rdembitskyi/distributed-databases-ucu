import time
import json
import csv
import io
import logging

from google.cloud import storage, pubsub_v1

from producer.config import GCS_BUCKET, GCS_PREFIX, PROJECT_ID, TOPIC_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def publish_blob(blob, publisher, topic_path):
    content = blob.download_as_text()
    reader = csv.DictReader(io.StringIO(content))
    row_count = 0
    int_fields = {"step", "isFraud", "isFlaggedFraud"}
    float_fields = {"amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"}
    for row in reader:
        for k in int_fields:
            row[k] = int(row[k])
        for k in float_fields:
            row[k] = float(row[k])
        message = json.dumps(row).encode("utf-8")
        publisher.publish(topic_path, data=message)
        row_count += 1
    logger.info("Published %d rows from %s", row_count, blob.name)


def main():
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    pages = bucket.list_blobs(prefix=GCS_PREFIX, page_size=2).pages

    for page in pages:
        blobs = list(page)
        logger.info("Fetched batch of %d files", len(blobs))
        for blob in blobs:
            if blob.name.endswith("/"):
                continue
            publish_blob(blob, publisher, topic_path)

        logger.info("Done publishing. Starting subscriber...")
        time.sleep(10)
    logger.info("Finished..")


if __name__ == "__main__":
    main()