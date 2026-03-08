resource "aws_s3_bucket" "standardized_bucket" {
  # This combines your inputs into a strict naming convention
  bucket = "tachpae-${var.environment}-${var.bucket_name}"

  tags = {
    SecurityLevel = "High"
    ManagedBy     = "Terraform-Blueprint"
  }
}