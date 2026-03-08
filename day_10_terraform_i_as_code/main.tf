provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  description = "enviroment (dev, staging, prod etc)"
  type = string
  default = "dev"
}

locals {
  team_name   = "data-engineering"
  project     = "tachpae-core"
  # You can combine strings dynamically here
  bucket_name = "${local.project}-${var.environment}-logs"
}

resource "aws_s3_bucket" "tachpe_logs_bucket" {
  # bucket = "tachpae-${var.environment}-logs-bucket"

  bucket = local.bucket_name
  
  tags = {
    Team        = local.team_name
    Environment = var.environment
  }
}

resource "aws_iam_policy" "iam_policy" {
  name = "tachpae-s3-reading"
  description = "this allows de to read logs bucket"

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [{
      Sid: "statemtn1",
      Effect: "Allow",
      Action: ["s3:ListBucket", "s3:GetObject"],
      Resource: [
        aws_s3_bucket.tachpe_logs_bucket.arn,
        "${aws_s3_bucket.tachpe_logs_bucket.arn}/*"
      ]
    }]
  })
}

# You call the blueprint here!
module "secure_tachpae_bucket" {
  source      = "./modules/secure-s3-blueprint"
  
  # You pass in the values for the variables it asked for
  environment = "prod"
  bucket_name = "event-ticket-data"
}

output "s3_bucket_arn" {
  description = "The ARN of the newly created logs bucket"
  value = aws_s3_bucket.tachpe_logs_bucket.arn
}