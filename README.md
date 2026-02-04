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

## Note on Project Intent

**This project is intentionally designed as a hands-on learning resource for students and practitioners who want to understand cloud-based data engineering through practice, not theory.**

It provides:
- An **end-to-end view** of how a data engineering project is structured
- Clear, incremental steps showing how pipelines are:
  - Designed
  - Implemented locally
  - Tested
  - Deployed and operated on the cloud

This repository does **not** aim to explain data engineering concepts in theory (e.g., what is ETL, topics related to storage and abstractions, what is schema evolution, or what is data quality etc). Those topics are assumed to be learned elsewhere. The focus here is purely **practical execution and workflow understanding**.

Each commit represents a **meaningful progression** in the project:
- How the repository structure evolves
- How components are added and wired together
- How local testing transitions into cloud deployment
- How validation and failure handling are introduced in real systems

The complexity of data engineering always depends on the use case. This project keeps the scope intentionally manageable, while still being realistic enough to demonstrate how a **production-style, end-to-end data pipeline** is built and operated in the cloud.

Treat this repository as a **reference implementation**—a concrete example of how the pieces fit together, rather than a universal blueprint.

---

## Steps Followed in the Project

### Step 0: **Initial Setup & Local Development**
**Goal**: Establish a reproducible local development environment and validate core pipeline logic before touching the cloud.

**What was done**:
- Set up a local Python development environment using **Poetry**.
- Defined a clear project structure aligned with future AWS deployment.
- Implemented a **local streaming-style ingestion pipeline** using a stubbed market data provider.
- Introduced a **canonical curated schema** to normalize provider data.
- Integrated **Great Expectations (GE)** to enforce data quality rules early in the pipeline.

**Key design decision**:
> Data quality validation is treated as a **hard gate**, ensuring data quality.

**Status**: ✅ DONE

---

### Step 1: Local Streaming Pipeline (Raw → Curated → Quality Gate)

**Goal**: Prove the end-to-end streaming logic locally before deploying to AWS.

#### Pipeline Zones (Local)
- **Raw Zone** (`data/raw/`)
  - Provider-format data (JSONL)
  - No assumptions, no validation
- **Curated Zone** (`data/curated/`)
  - Cleaned and standardized records
  - Stable schema used across the system
- **Quarantine Zone** (`data/quarantine/`)
  - Records that fail data quality checks
  - Preserved for inspection and debugging

#### Pipeline Flow
1. Fetch simulated price data from a provider stub.
2. Write raw data to the raw zone.
3. Transform raw data into the curated schema.
4. Validate curated data using **Great Expectations**.
5. Route data:
   - **PASS** → curated zone
   - **FAIL** → quarantine zone

This local flow mirrors the **exact architecture** later deployed to AWS.

**Status**:
- **TASK-01**: Storage zone separation (raw / curated / quarantine): ✅ DONE  
- **TASK-02**: Great Expectations data quality gate: ✅ DONE  
- **TASK-03**: Pass/fail routing logic with quarantine handling: ✅ DONE  

---

### Step 2: AWS Infrastructure Provisioning (Terraform)

**Goal**: Provision production-grade cloud infrastructure using Infrastructure as Code, without deploying compute yet.

All infrastructure was created using **Terraform** to ensure repeatability and clarity.

#### Provisioned Resources
1. **S3 Bucket**
   - Single bucket with logical zones:
     - `raw/`
     - `curated/`
     - `quarantine/`
   - Versioning enabled
   - Server-side encryption enabled
   - Public access fully blocked

2. **DynamoDB Table**
   - Table name: `latest_prices`
   - Partition key: `symbol`
   - Billing mode: PAY_PER_REQUEST
   - Designed for low-latency “latest value per symbol” access

3. **IAM Role for Lambda**
   - Permissions to:
     - Write raw, curated, and quarantine data to S3
     - Write latest prices to DynamoDB
     - Emit logs to CloudWatch

4. **AWS Account & Tooling Setup**
   - AWS account secured with MFA
   - IAM user created for development
   - AWS CLI configured (`mdp-dev` profile)
   - Terraform initialized and validated

> At this stage, **no compute is running**, so cloud cost remains negligible.

**Status**:
- **TASK-01**: AWS account setup, IAM user, MFA, billing safeguards: ✅ DONE  
- **TASK-02**: Terraform infrastructure provisioning (S3, DynamoDB, IAM): ✅ DONE

---

### Step 3: Lambda Deployment & Cloud-Based Streaming Pipeline

**Goal**: Deploy the validated local streaming pipeline to AWS and execute it end-to-end in the cloud.

This step transitions the project from *local simulation* to a **production-style, cloud-executed streaming pipeline**, while preserving the same architectural guarantees:
raw → curated → quality-gated → serving.

#### What Was Implemented :

##### 1. Lambda Containerization
- Streaming ingestion pipeline packaged as an **AWS Lambda container image**
- Based on `public.ecr.aws/lambda/python:3.12`
- Dependencies installed at build time
- Build optimized using `.dockerignore`
- Single-architecture image (`linux/amd64`) to ensure Lambda compatibility

##### 2. Elastic Container Registry (ECR)
- ECR repository provisioned via Terraform
- Lambda image pushed to ECR
- Image-based deployment strategy adopted instead of ZIP packaging

##### 3. Lambda Function Deployment
- Lambda deployed via Terraform using `package_type = "Image"`
- Environment variables configured:
  - `S3_BUCKET_NAME`
  - `DDB_TABLE_LATEST_PRICES`
- IAM role attached with least-privilege permissions
- Memory and timeout tuned for streaming micro-batch workloads

##### 4. Streaming Execution Logic (Cloud)
- Fetch latest prices (stub provider for now)
- Normalize provider payload into a canonical schema
- Write **raw JSONL** batches to S3
- Apply **Great Expectations** data quality validation
- On **PASS**:
  - Write curated JSONL batch to S3
  - Upsert latest price per symbol into DynamoDB
- On **FAIL**:
  - Write curated batch to the S3 quarantine zone
  - Prevent invalid data from being served

##### 5. DynamoDB Integration
- DynamoDB used as an OLTP serving store for “latest price per symbol”
- Implemented float → `Decimal` conversion to meet DynamoDB type requirements
- Verified correct numeric storage and overwrite semantics

##### 6. Observability & Validation
- Lambda logs emitted to CloudWatch
- Manual invocation used to validate:
  - Lambda execution
  - S3 writes (raw, curated, quarantine)
  - DynamoDB updates
  - End-to-end cloud data flow correctness


#### Verified Outcomes :

- Lambda executes successfully in AWS
- Raw and curated data land in S3
- Data quality gate enforced in cloud execution
- Latest prices stored in DynamoDB with correct data types
- End-to-end streaming pipeline validated


#### Step 3 Status :

- **TASK-03.1**: Lambda containerization & ECR push — ✅ DONE  
- **TASK-03.2**: Lambda deployment via Terraform — ✅ DONE  
- **TASK-03.3**: Cloud execution of streaming pipeline — ✅ DONE  
- **TASK-03.4**: S3 + DynamoDB integration validated — ✅ DONE  
- **TASK-03.5**: EventBridge scheduler implemented and validated (reversible control via Terraform variables) — ✅ DONE  
- **TASK-03.6**: CloudWatch alarms + log retention configured (Errors + Throttles) — ✅ DONE  
- **TASK-03.7**: Quality marker added to Lambda logs (`QUALITY=PASS|FAIL`) for monitoring — ✅ DONE  

#### Remaining Work (Step 3 Continuation) :

- Add **CloudWatch log metric filter** + **alarm** for data quality failures (`QUALITY=FAIL`)
- Replace stub provider with real market data API
- Introduce AWS Secrets Manager for API credentials
- Add notification wiring (SNS) for alarms (optional, portfolio polish)

**Overall Step Status**: ⏳ In Progress (core pipeline complete, observability and real ingestion pending)

---

## Next Big Steps
1. **Provider API Integration**: Replacing the stub with a real API for fetching market data (e.g., Alpha Vantage, Yahoo Finance).
2. **Batch Processing**: Implementing batch pipelines to process historical data and aggregate it for deeper analytics.
3. **Machine Learning**: Integrating machine learning models for price prediction.
4. **UI Integration**: Building a lightweight frontend to view stock data and analytics.
5. **Cost Optimization**: Fine-tuning AWS resources for lower cost.

---

## Technologies Used So Far
- **AWS Lambda**
- **Elastic Container Registry(ECR)**
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

## Security Note
```bash
- Secrets and environment-specific configuration are intentionally excluded.
- See .env.example and terraform.tfvars.example for required variables.
```

---

## License
This project is licensed under the company "Fourth-Projection".



