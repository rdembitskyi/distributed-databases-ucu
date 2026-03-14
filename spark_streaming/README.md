# Spark Streaming - Fraud Detection Pipeline

Pipeline that streams fraud detection data through GCP Pub/Sub into BigQuery using Spark Structured Streaming.

## Architecture

```
GCS (CSV files) → Producer → Pub/Sub Topic → Subscription → GCS (JSON) → Spark Streaming → BigQuery
```

1. **Producer** reads CSV files from a public GCS bucket and publishes rows as JSON messages to a Pub/Sub topic
2. **Pub/Sub subscription** writes messages as JSON files into a GCS bucket
3. **Consumer** (Spark Structured Streaming) watches the bucket for new JSON files, reads them, and writes to a BigQuery table

## Setup

### 1. Authenticate and set up GCP resources

```bash
gcloud auth login
gcloud auth application-default login

# install dependecies
pip install -r requirements.txt

# Create Pub/Sub topic
gcloud pubsub topics create fraud-detection

# Create subscription that writes to your bucket (set up via GCP Console UI:
# Pub/Sub > Subscriptions > Create > Delivery type: Write to Cloud Storage)

# Create BigQuery dataset and table
bq mk --dataset spring-melody-472217-a1:streaming
bq mk --table spring-melody-472217-a1:streaming.fraud_transactions \
  step:INTEGER,type:STRING,amount:FLOAT,nameOrig:STRING,oldbalanceOrg:FLOAT,newbalanceOrig:FLOAT,nameDest:STRING,oldbalanceDest:FLOAT,newbalanceDest:FLOAT,isFraud:INTEGER,isFlaggedFraud:INTEGER
```

## Running

### Producer (locally)

From the `spark_streaming/` directory:

```bash
pip install -r requirements.txt
python -m producer.logic
```

This reads CSVs from `gs://oklev-uku-datasets/fraud-detection-splitted/`, converts rows to JSON with proper types, and publishes them to the `fraud-detection` Pub/Sub topic.

### Consumer (on Dataproc)

Run in a Dataproc interactive session (Spark Connect):

```python
from google.cloud.dataproc_spark_connect import DataprocSparkSession
from google.cloud.dataproc_v1 import Session

session = Session()
spark = DataprocSparkSession.builder \
    .appName("fraud_detection_stream") \
    .dataprocSessionConfig(session) \
    .getOrCreate()
```

Then execute the consumer code from `scripts/consumer.py`. It watches `gs://rd-ucu-bucket/` for new JSON files and writes them to BigQuery table `streaming.fraud_transactions`.

## Data Schema

You can find it in consumer

```bash
bq rm -r -f spring-melody-472217-a1:streaming
gcloud pubsub subscriptions delete fraud-detection-sub
gcloud pubsub topics delete fraud-detection
```