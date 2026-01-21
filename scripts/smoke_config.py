import sys
from pathlib import Path

# Add repo root to PYTHONPATH so imports work when running scripts directly
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from pipelines.streaming.ingest_lambda.config import settings  # noqa: E402


def main():
    print("Config loaded.")
    print("AWS_REGION:", settings.aws_region)
    print("DATA_PROVIDER:", settings.data_provider)
    print("S3_BUCKET_RAW set:", bool(settings.s3_bucket_raw))
    print("DDB_TABLE_LATEST_PRICES set:", bool(settings.ddb_table_latest_prices))


if __name__ == "__main__":
    main()
