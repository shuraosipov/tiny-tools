resource "aws_cloudfront_distribution" "statgpt2_distribution" {
  origin {
    domain_name = aws_s3_bucket.statgpt2_bucket.bucket_regional_domain_name
    origin_id   = "S3Origin"

    # Optional: Configure origin access identity for S3
    origin_access_identity = aws_cloudfront_origin_access_identity.statgpt2_oai.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Cache behavior settings
  default_cache_behavior {
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  # SSL certificate configuration
  viewer_certificate {
    acm_certificate_arn = var.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  # Geo-restriction settings (optional)
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Logging configuration
  logging_config {
    bucket         = aws_s3_bucket.logging_bucket.bucket_regional_domain_name
    include_cookies = false
    prefix         = "cloudfront-logs/"
  }

  # Tags for resource organization
  tags = {
    Name        = "StatGPT2-CloudFront"
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "statgpt2_bucket" {
  bucket = "statgpt2-bucket-${var.environment}"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name        = "StatGPT2-Bucket"
    Environment = var.environment
  }
}

resource "aws_cloudfront_origin_access_identity" "statgpt2_oai" {
  comment = "Origin Access Identity for StatGPT2 S3 Bucket"
}

resource "aws_s3_bucket" "logging_bucket" {
  bucket = "statgpt2-logs-${var.environment}"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name        = "StatGPT2-Logging-Bucket"
    Environment = var.environment
  }
}