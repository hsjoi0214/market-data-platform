# Learning Header
# Learning Track: Batch
# Learning Step: 2 of 5
# Checklist Categories: 3. Compute / Processing, 5. Permissions / IAM, 6. Configuration / Secrets
# Purpose: Deploy the batch extract Lambda that calls Alpha Vantage and lands raw historical JSONL into S3.

# ----------------------------------------
# Batch extract Lambda IAM
# ----------------------------------------

resource "aws_iam_role" "batch_extract_lambda_role" {
  name = "${var.project_name}-${var.environment}-batch-extract-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "batch_extract_lambda_policy" {
  name = "${var.project_name}-${var.environment}-batch-extract-policy"
  role = aws_iam_role.batch_extract_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.raw_bucket.arn}/raw/prices_daily/*"
        ]
      },
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:secretsmanager:${var.region}:582997419489:secret:mdp/market-data/${var.environment}/provider_api_key*"
      },
      {
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# ----------------------------------------
# Batch extract Lambda
# ----------------------------------------

resource "aws_lambda_function" "batch_extract" {
  function_name = "${var.project_name}-${var.environment}-batch-extract"
  role          = aws_iam_role.batch_extract_lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.streaming_ingest.repository_url}:${var.lambda_image_tag}"

  timeout     = 180
  memory_size = 512

  image_config {
    command = ["pipelines.batch.ohlc_daily.extract_lambda.lambda_handler"]
  }

  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.raw_bucket.bucket
      PROVIDER_SECRET_ID  = "mdp/market-data/${var.environment}/provider_api_key"
      BATCH_MODE          = "incremental"
      BATCH_SYMBOLS       = "AAPL,MSFT"
      BATCH_BACKFILL_DAYS = "90"
      BATCH_LOOKBACK_DAYS = "10"
    }
  }

  tags = {
    Name        = "${var.project_name}-batch-extract"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [aws_ecr_repository.streaming_ingest]
}

resource "aws_cloudwatch_log_group" "lambda_batch_extract" {
  name              = "/aws/lambda/${aws_lambda_function.batch_extract.function_name}"
  retention_in_days = 7

  depends_on = [aws_lambda_function.batch_extract]

  tags = {
    Name        = "${var.project_name}-batch-extract-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}
