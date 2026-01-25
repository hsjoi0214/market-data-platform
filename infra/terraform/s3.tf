resource "aws_s3_bucket" "raw_bucket" {
  bucket = "${var.project_name}-${var.environment}-${var.region}-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "mdp-market-data-bucket"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Enable versioning (separate resource in newer provider patterns)
resource "aws_s3_bucket_versioning" "raw_bucket_versioning" {
  bucket = aws_s3_bucket.raw_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Block ALL public access (separate resource)
resource "aws_s3_bucket_public_access_block" "raw_bucket_pab" {
  bucket = aws_s3_bucket.raw_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Recommended: enforce bucket owner ownership for objects
resource "aws_s3_bucket_ownership_controls" "raw_bucket_owner" {
  bucket = aws_s3_bucket.raw_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# server-side encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_bucket_sse" {
  bucket = aws_s3_bucket.raw_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- Prefix placeholders ---
# ACLs are not used with BucketOwnerEnforced.
resource "aws_s3_object" "raw_prices" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "raw/prices/"
}

resource "aws_s3_object" "curated_prices" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "curated/prices/"
}

resource "aws_s3_object" "quarantine_streaming" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "quarantine/streaming/"
}