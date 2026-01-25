resource "aws_dynamodb_table" "latest_prices" {
  name         = "latest_prices"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "symbol"

  attribute {
    name = "symbol"
    type = "S"
  }

  tags = {
    Name        = "Latest Prices Table"
    Environment = var.environment
    Project     = var.project_name
  }
}