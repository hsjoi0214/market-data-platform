# ----------------------------------------
# Batch S3 prefix placeholders
# ----------------------------------------

resource "aws_s3_object" "raw_prices_daily" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "raw/prices_daily/"
}

resource "aws_s3_object" "curated_prices_daily" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "curated/prices_daily/"
}

resource "aws_s3_object" "analytics_ohlc_daily" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "analytics/ohlc_daily/"
}

resource "aws_s3_object" "quarantine_batch_ohlc_daily" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "quarantine/batch/ohlc_daily/"
}

resource "aws_s3_object" "athena_results" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "athena/results/"
}