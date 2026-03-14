import logging
from producer.config import PROJECT_ID, TOPIC_ID

from google.cloud import pubsub_v1

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

logger.info("Creating Pub/Sub topic %s in project %s", TOPIC_ID, PROJECT_ID)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
topic = publisher.create_topic(request={"name": topic_path})

logger.info("Created topic: %s", topic.name)