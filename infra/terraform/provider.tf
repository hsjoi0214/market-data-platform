# Learning Header
# Read Order: 01
# Checklist Categories: 9. Environment / Delivery
# Purpose: Configure the AWS provider and generate a stable random suffix for globally unique resource names.

provider "aws" {
  profile = "mdp-dev"
  region  = "us-east-1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
