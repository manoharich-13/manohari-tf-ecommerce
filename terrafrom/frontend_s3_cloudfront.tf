# Frontend hosting: S3 (private) + CloudFront (public) for static HTML

# --------------------
# Inputs
# --------------------
variable "frontend_bucket_suffix" {
  description = "Random/unique suffix for S3 bucket name to ensure uniqueness."
  type        = string
  default     = "static"
}

# --------------------
# S3 bucket (private)
# --------------------
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_prefix}-frontend-${var.frontend_bucket_suffix}-${data.aws_caller_identity.current.account_id}"
}

# NOTE: Do not manage aws_s3_bucket_public_access_block here.
# Your AWS Organization SCP explicitly denies s3:PutBucketPublicAccessBlock.
# The bucket policy + CloudFront OAC is sufficient for private access.

# Ensure bucket owner enforced (recommended when using CloudFront/OAC)

resource "aws_s3_bucket_ownership_controls" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# --------------------
# OAC (Origin Access Control)
# --------------------
resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "${var.project_prefix}-frontend-oac"
  description                       = "OAC for private S3 frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# --------------------
# Upload frontend files to S3 using aws_s3_object
# --------------------
locals {
  frontend_dir = "../frontend"

  # Find all files under frontend/ and create a map of
  # relative_path -> absolute_path
  frontend_files = fileset(local.frontend_dir, "**/*")

  frontend_objects = {
    for rel in local.frontend_files :
    rel => {
      source_path = "${local.frontend_dir}/${rel}"

      content_type = (
        endswith(rel, ".html") ? "text/html" :
        endswith(rel, ".css") ? "text/css" :
        endswith(rel, ".js") ? "application/javascript" :
        endswith(rel, ".json") ? "application/json" :
        endswith(rel, ".png") ? "image/png" :
        endswith(rel, ".jpg") ? "image/jpeg" :
        endswith(rel, ".jpeg") ? "image/jpeg" :
        endswith(rel, ".svg") ? "image/svg+xml" :
        "application/octet-stream"
      )
    }
    if !endswith(rel, "/")
  }
}

resource "aws_s3_object" "frontend_objects" {
  for_each = local.frontend_objects

  bucket       = aws_s3_bucket.frontend.id
  key          = each.key
  source       = each.value.source_path
  content_type = each.value.content_type
  cache_control = "max-age=0, no-cache, no-store, must-revalidate"

  etag = filemd5(each.value.source_path)

  depends_on = [aws_s3_bucket_ownership_controls.frontend]
}

# Bucket policy allowing CloudFront OAC to read objects
resource "aws_s3_bucket_policy" "frontend_policy" {
  bucket = aws_s3_bucket.frontend.id

  depends_on = [aws_cloudfront_origin_access_control.oac]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontRead"
        Effect    = "Allow"
        Principal = { Service = "cloudfront.amazonaws.com" }
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}

# --------------------
# CloudFront managed policies
# --------------------
data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

# Use a known AWS managed origin request policy name.
# If your AWS environment doesn't have it, we can switch to a custom aws_cloudfront_origin_request_policy resource.
data "aws_cloudfront_origin_request_policy" "blank_origin" {
  name = "Managed-CORS-S3Origin"
}



# --------------------
# CloudFront distribution
# --------------------
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  comment             = "Static frontend for ${var.project_prefix}"
  default_root_object = "manohari-tf-login.html"

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "s3-${aws_s3_bucket.frontend.id}"

    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-${aws_s3_bucket.frontend.id}"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    compress = true

    # Use AWS managed policies (avoid hard-coded IDs that may not exist in your account/region)
    # If your account doesn't have these managed policies, Terraform will fail here (then we can create explicit policies).
    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_optimized.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.blank_origin.id

  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  depends_on = [aws_s3_object.frontend_objects]
}

resource "null_resource" "cloudfront_invalidation" {
  provisioner "local-exec" {
    command = "powershell -Command \"if (Get-Command aws -ErrorAction SilentlyContinue) { try { aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend.id} --paths '/*' } catch { Write-Output 'AWS invalidation skipped: credentials not configured'; exit 0 } } else { Write-Output 'AWS CLI not found, skipping invalidation'; exit 0 }\""
  }

  triggers = {
    distribution_id = aws_cloudfront_distribution.frontend.id
    object_etags     = join(",", [for obj in aws_s3_object.frontend_objects : obj.etag])
  }
}

output "cloudfront_frontend_url" {
  value = "https://${aws_cloudfront_distribution.frontend.domain_name}/"
}

