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

output "batch_extract_lambda_name" {
  value       = aws_lambda_function.batch_extract.function_name
  description = "The batch extract Lambda function name"
}
