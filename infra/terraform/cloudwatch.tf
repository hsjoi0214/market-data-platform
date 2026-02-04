# Creates a CloudWatch log group for our Lambda function and sets how long logs are kept.
resource "aws_cloudwatch_log_group" "lambda_streaming_ingest" {
  name              = "/aws/lambda/${aws_lambda_function.streaming_ingest.function_name}"
  retention_in_days = 7

  # Ensure Lambda exists first
  depends_on = [aws_lambda_function.streaming_ingest]

  tags = {
    Name        = "${var.project_name}-streaming-ingest-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Monitors our Lambda for errors and triggers an alert/alarm if any errors occur.
resource "aws_cloudwatch_metric_alarm" "lambda_streaming_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-streaming-lambda-errors"
  alarm_description   = "Triggers if the streaming ingest Lambda reports any errors."
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.streaming_ingest.function_name
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

#  Monitors if our Lambda is being throttled (hitting concurrency/burst limits) and alerts us.
resource "aws_cloudwatch_metric_alarm" "lambda_streaming_throttles" {
  alarm_name          = "${var.project_name}-${var.environment}-streaming-lambda-throttles"
  alarm_description   = "Triggers if the streaming ingest Lambda is throttled."
  namespace           = "AWS/Lambda"
  metric_name         = "Throttles"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.streaming_ingest.function_name
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# With this file we can clearly see that Group 1 manages logs, Group 2 catches errors, Group 3 catches performance problems (throttling).