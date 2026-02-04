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