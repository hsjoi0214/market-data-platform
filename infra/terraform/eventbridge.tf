resource "aws_cloudwatch_event_rule" "streaming_schedule" {
  count               = var.schedule_enabled ? 1 : 0
  name                = "${var.project_name}-${var.environment}-streaming-schedule"
  description         = "Schedule streaming ingest Lambda"
  schedule_expression = "rate(${var.schedule_rate_minutes} minutes)"
}

resource "aws_lambda_permission" "allow_eventbridge" {
  count         = var.schedule_enabled ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.streaming_ingest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.streaming_schedule[0].arn
}

resource "aws_cloudwatch_event_target" "streaming_lambda_target" {
  count = var.schedule_enabled ? 1 : 0
  rule  = aws_cloudwatch_event_rule.streaming_schedule[0].name
  arn   = aws_lambda_function.streaming_ingest.arn
}



# Three AWS resources (only when schedule_enabled=true)
# - an EventBridge rule: rate(2 minutes)
# - a Lambda permission: allows events.amazonaws.com to invoke our Lambda
# - an EventBridge target: connects the rule → our Lambda