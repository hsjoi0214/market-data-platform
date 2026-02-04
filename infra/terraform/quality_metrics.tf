############################################
# Data quality monitoring (GE FAIL)
############################################

resource "aws_cloudwatch_metric_alarm" "quality_fail_alarm" {
  count               = var.schedule_enabled ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-quality-fail"
  alarm_description   = "Triggers if any data quality failures occur (QualityFailCount > 0)."
  namespace           = "MDP/Quality"
  metric_name         = "QualityFailCount"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

############################################
# Storage liveness monitoring (RAW writes)
############################################

resource "aws_cloudwatch_metric_alarm" "storage_raw_freshness_alarm" {
  count               = var.schedule_enabled ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-storage-raw-freshness"
  alarm_description   = "Triggers if no raw S3 write is observed in the last 10 minutes (StorageRawWriteCount < 1)."
  namespace           = "MDP/Storage"
  metric_name         = "StorageRawWriteCount"
  statistic           = "Sum"
  period              = 600 # 10 minutes
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "LessThanThreshold"

  # If scheduler is enabled and we see no raw writes, that's a problem.
  treat_missing_data = "breaching"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}