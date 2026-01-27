resource "aws_ecr_repository" "streaming_ingest" {
  name                 = "${var.project_name}-${var.environment}-streaming-ingest"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-streaming-ingest"
    Environment = var.environment
    Project     = var.project_name
  }
}

output "ecr_repo_url" {
  value       = aws_ecr_repository.streaming_ingest.repository_url
  description = "ECR repository URL (use this to tag and push Docker images)"
}