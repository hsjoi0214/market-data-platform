resource "aws_s3_bucket" "raw_bucket" {
  bucket = "${var.project_name}-${var.environment}-${var.region}-${random_id.bucket_suffix.hex}"
  acl    = "private"

  tags = {
    Name        = "Raw Data Bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_object" "raw_prices" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "raw/prices/"
  acl    = "private"
}

resource "aws_s3_bucket_object" "curated_prices" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "curated/prices/"
  acl    = "private"
}
