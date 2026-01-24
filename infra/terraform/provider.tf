provider "aws" {
  profile = "mdp-dev"
  region  = "us-east-1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}