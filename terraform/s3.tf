resource "aws_s3_bucket" "its_s3" {
  for_each = var.environment == "staging" ? 1 : 0
  bucket   = "pbs.its-${var.environment}.storage.${var.account}"
  acl      = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id                                     = "CleanupMultiParts"
    enabled                                = true
    abort_incomplete_multipart_upload_days = 3
  }
  tags = {
    Name    = "its-${var.environment}"
    Creator = "Terraform"
  }
}