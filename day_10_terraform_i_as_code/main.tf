provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "tachpe_logs_bucket" {
  bucket = "tachpae-de-logs-bucket"
}

resource "aws_iam_policy" "iam_policy" {
  name = "tachpae-s3-reading"
  description = "this allows de to read logs bucket"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "statemtn1",
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetObject"],
      "Resource": [
        aws_s3_bucket.tachpe_logs_bucket.arn,
        "${aws_s3_bucket.tachpe_logs_bucket.arn}/*"
      ]
    }]
  })
}