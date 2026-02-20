resource "aws_lambda_function" "streaming_ingest" {
  function_name = "${var.project_name}-${var.environment}-streaming-ingest"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.streaming_ingest.repository_url}:${var.lambda_image_tag}"

  timeout     = 60
  memory_size = 512

  environment {
    variables = {
      S3_BUCKET_NAME          = aws_s3_bucket.raw_bucket.bucket
      DDB_TABLE_LATEST_PRICES = aws_dynamodb_table.latest_prices.name
      PROVIDER_SECRET_ID      = "mdp/market-data/${var.environment}/provider_api_key"
    }
  }

  tags = {
    Name        = "${var.project_name}-streaming-ingest"
    Environment = var.environment
    Project     = var.project_name
  }

  # Important: Lambda must wait until the repo exists
  depends_on = [aws_ecr_repository.streaming_ingest]
}

# chain of responsibility can be seen here as : eventbridge gets activated and points to lambda ARN, 
# then this file points to the ecr_image and then lambda services pulls from ecr when needed. 

