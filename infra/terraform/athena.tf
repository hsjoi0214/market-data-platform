# Learning Header
# Learning Track: Batch
# Learning Step: 5 of 5
# Checklist Categories: 3. Compute / Processing, 4. Persistence / Data Stores, 7. Observability / Operations
# Purpose: Configure the Athena workgroup that queries the analytics zone and stores query results in S3.

# ----------------------------------------
# Athena Workgroup
# ----------------------------------------

resource "aws_athena_workgroup" "batch_queries" {
  name = "${var.project_name}-${var.environment}-athena"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.raw_bucket.bucket}/athena/results/"
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
