import logging

from google.cloud.dataproc_spark_connect import DataprocSparkSession
from google.cloud.dataproc_v1 import Session
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BIGQUERY_TABLE = "streaming.fraud_transactions"

session = Session()

spark = DataprocSparkSession.builder \
    .appName("fraud_detection_stream") \
    .projectId("spring-melody-472217-a1") \
    .location('us-central1') \
    .dataprocSessionConfig(session) \
    .getOrCreate()

schema = StructType([
    StructField("step", IntegerType(), True),
    StructField("type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("nameOrig", StringType(), True),
    StructField("oldbalanceOrg", DoubleType(), True),
    StructField("newbalanceOrig", DoubleType(), True),
    StructField("nameDest", StringType(), True),
    StructField("oldbalanceDest", DoubleType(), True),
    StructField("newbalanceDest", DoubleType(), True),
    StructField("isFraud", IntegerType(), True),
    StructField("isFlaggedFraud", IntegerType(), True),
])


def process_batch(batch_df, batch_id):
    logger.info("Batch %d: %d records", batch_id, batch_df.count())
    batch_df.show(truncate=False)
    batch_df.write \
        .format("bigquery") \
        .option("table", BIGQUERY_TABLE) \
        .option("writeMethod", "direct") \
        .mode("append") \
        .save()
    logger.info("Batch %d written to BigQuery", batch_id)


df = spark \
    .readStream \
    .format("json") \
    .schema(schema) \
    .load("gs://rd-ucu-bucket/")

query = df.writeStream \
    .foreachBatch(process_batch) \
    .trigger(processingTime="5 seconds") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/fraud_stream_checkpoint") \
    .start()

logger.info("Streaming started, waiting for termination...")
query.awaitTermination(120)