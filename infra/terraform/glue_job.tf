# Learning Header
# Learning Track: Batch
# Learning Step: 3 of 5
# Checklist Categories: 3. Compute / Processing, 5. Permissions / IAM, 4. Persistence / Data Stores
# Purpose: Deploy the Glue transform job that reads raw daily data from S3 and writes curated and analytics Parquet outputs.

# ----------------------------------------
# Glue IAM role
# ----------------------------------------

resource "aws_iam_role" "glue_job_role" {
  name = "${var.project_name}-${var.environment}-glue-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# AWS-managed baseline policy for Glue service roles
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Project-specific S3 access for batch zones + Athena results + script location
resource "aws_iam_role_policy" "glue_job_s3_policy" {
  name = "${var.project_name}-${var.environment}-glue-job-s3-policy"
  role = aws_iam_role.glue_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.raw_bucket.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.raw_bucket.arn}/*"
        ]
      }
    ]
  })
}

# ----------------------------------------
# S3 prefix for Glue scripts
# ----------------------------------------

resource "aws_s3_object" "glue_scripts_prefix" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "glue/scripts/"
}

# Upload the Glue script from local repo to S3
resource "aws_s3_object" "batch_ohlc_glue_script" {
  bucket = aws_s3_bucket.raw_bucket.bucket
  key    = "glue/scripts/batch_ohlc_daily_glue_job.py"
  source = "${path.module}/../../pipelines/batch/ohlc_daily/cloud/glue_job.py"
  etag   = filemd5("${path.module}/../../pipelines/batch/ohlc_daily/cloud/glue_job.py")
}

# ----------------------------------------
# Glue Job
# ----------------------------------------

resource "aws_glue_job" "batch_ohlc_daily" {
  name     = "${var.project_name}-${var.environment}-batch-ohlc-daily"
  role_arn = aws_iam_role.glue_job_role.arn

  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
  max_retries       = 0
  timeout           = 10

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.raw_bucket.bucket}/${aws_s3_object.batch_ohlc_glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
    "--TempDir"                          = "s3://${aws_s3_bucket.raw_bucket.bucket}/glue/temp/"
    "--RAW_INPUT_PATH"                   = "s3://${aws_s3_bucket.raw_bucket.bucket}/raw/prices_daily/"
    "--CURATED_OUTPUT_PATH"              = "s3://${aws_s3_bucket.raw_bucket.bucket}/curated/prices_daily/"
    "--ANALYTICS_OUTPUT_PATH"            = "s3://${aws_s3_bucket.raw_bucket.bucket}/analytics/ohlc_daily/"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [
    aws_iam_role_policy_attachment.glue_service_role,
    aws_iam_role_policy.glue_job_s3_policy,
    aws_s3_object.batch_ohlc_glue_script
  ]
}
