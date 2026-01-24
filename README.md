# Market Data Platform - Cloud Data Engineering Project

## Overview

This project implements a **cloud-native data engineering platform** focused on **market data**. The platform ingests financial market data (like stock prices) in near real-time, cleans and validates it, stores the cleaned data in DynamoDB, and handles failed data through quarantine storage in S3.

Key components:
- **AWS Lambda**: To process and transform data.
- **EventBridge**: To trigger Lambda functions at fixed intervals.
- **S3**: To store raw, curated, and quarantine data.
- **DynamoDB**: To store the latest price data.
- **Great Expectations**: To validate the data before it is inserted into DynamoDB.

---

## Steps Followed in the Project

### Step 0: **Initial Setup & Local Development**
- Set up a local environment for testing using **Python** and **Poetry**.
- Created a basic **streaming pipeline** where data is fetched from a stubbed provider, cleaned, and validated using **Great Expectations (GE)**.
- Implemented data quality checks to ensure that only valid data is passed into the final system.

---

### Step 1: **Local Streaming Pipeline**
- **Raw Data**: The raw data is fetched from a provider stub, simulating stock prices.
- **Curated Data**: The raw data is standardized into a stable format, cleaning it into the **curated schema**.
- **Great Expectations Gate**: The curated data is validated using **GE**. If the data passes, it moves on to the next stage; if it fails, it is routed to a quarantine location.
- **Quarantine**: Invalid data is stored in S3 for further investigation.

**Local pipeline flow**:
1. Data is fetched and stored in the `data/raw/` folder.
2. Data is cleaned and stored in the `data/curated/` folder.
3. If validation fails, data is routed to the `data/quarantine/` folder.

---

### Step 2: **AWS Infrastructure (Terraform)**
The AWS infrastructure was provisioned using **Terraform** for:
1. **S3 Bucket**: To store raw, curated, and quarantine data.
2. **DynamoDB Table**: To store the latest prices with a partition key of `symbol`.
3. **IAM Role**: Lambda functions were given permission to access the S3 bucket and DynamoDB table.
4. **EventBridge**: Set up to trigger Lambda functions at 1-minute intervals.

### AWS Architecture:
- **S3 Bucket**: Stores raw data, curated data, and quarantine data.
- **DynamoDB**: Stores the latest price data.
- **Lambda**: Processes the data, validates it using GE, and stores it in DynamoDB or quarantines it if invalid.
- **EventBridge**: Triggers the Lambda function every minute to simulate near-real-time data ingestion.

---

## Next Steps
1. **Provider API Integration**: Replacing the stub with a real API for fetching market data (e.g., Alpha Vantage, Yahoo Finance).
2. **Batch Processing**: Implementing batch pipelines to process historical data and aggregate it for deeper analytics.
3. **Machine Learning**: Integrating machine learning models for price prediction.
4. **UI Integration**: Building a lightweight frontend to view stock data and analytics.
5. **Cost Optimization**: Fine-tuning AWS resources for lower cost.

---

## Technologies Used So Far
- **AWS Lambda**
- **EventBridge**
- **S3**
- **DynamoDB**
- **Terraform**
- **Great Expectations**
- **Poetry + Python** (for local development)

---

## How to Run Locally
1. Install dependencies using **Poetry**:
    ```bash
    poetry install
    ```
2. Run the streaming pipeline locally:
    ```bash
    poetry run python -m pipelines.streaming.ingest_lambda.app
    ```

---

## License
This project is licensed under the Fourth-Projection.



