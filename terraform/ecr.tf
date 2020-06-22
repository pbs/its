############################################################################
# ECR
############################################################################

resource "aws_ecr_repository" "its_ecr" {
  name                 = "its-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name    = "its-${var.environment}"
    Creator = "Terraform"
  }
}