output "s3_bucket_name" {
  value       = aws_s3_bucket.raw_bucket.bucket
  description = "The S3 bucket name"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.latest_prices.name
  description = "The DynamoDB table name"
}

output "lambda_role_arn" {
  value       = aws_iam_role.lambda_role.arn
  description = "The IAM role ARN for Lambda"
}