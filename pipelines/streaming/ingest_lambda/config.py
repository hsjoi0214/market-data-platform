import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    data_provider: str = os.getenv("DATA_PROVIDER", "alphavantage")

    # Secrets Manager secret id (AWS)
    provider_secret_id: str = os.getenv("PROVIDER_SECRET_ID", "")

    # Local dev fallback (optional)
    alphavantage_api_key: str = os.getenv("ALPHAVANTAGE_API_KEY", "")

    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "")
    ddb_table_latest_prices: str = os.getenv("DDB_TABLE_LATEST_PRICES", "")


settings = Settings()