resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

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
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["s3:GetObject", "s3:PutObject"]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.raw_bucket.arn}/raw/*",
          "${aws_s3_bucket.raw_bucket.arn}/curated/*",
          "${aws_s3_bucket.raw_bucket.arn}/quarantine/*"
        ]
      },
      {
        Action   = ["dynamodb:PutItem"]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.latest_prices.arn
      },
      {
        # Allow publishing custom CloudWatch metrics (PutMetricData has no resource-level ARNs)
        Action   = ["cloudwatch:PutMetricData"]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:secretsmanager:${var.region}:582997419489:secret:mdp/market-data/${var.environment}/provider_api_key*"
      }
    ]
  })
}