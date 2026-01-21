import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    data_provider: str = os.getenv("DATA_PROVIDER", "unknown")
    price_api_key: str = os.getenv("PRICE_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")

    s3_bucket_raw: str = os.getenv("S3_BUCKET_RAW", "")
    ddb_table_latest_prices: str = os.getenv("DDB_TABLE_LATEST_PRICES", "")


settings = Settings()
