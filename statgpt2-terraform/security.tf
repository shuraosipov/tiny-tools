resource "aws_security_group" "statgpt2_sg" {
  name        = "statgpt2_security_group"
  description = "Security group for StatGPT 2.0 application"
  vpc_id     = aws_vpc.statgpt2_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow HTTPS traffic from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "statgpt2_security_group"
    Environment = var.environment
  }
}

resource "aws_iam_role" "statgpt2_ecs_task_role" {
  name               = "statgpt2_ecs_task_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json

  tags = {
    Name        = "statgpt2_ecs_task_role"
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "statgpt2_ecs_task_policy" {
  name        = "statgpt2_ecs_task_policy"
  description = "Policy for ECS tasks to access necessary resources"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "rds:DescribeDBInstances",
          "es:ESHttpGet",
          "es:ESHttpPut",
          "elasticache:DescribeCacheClusters"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "statgpt2_ecs_task_policy"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "attach_ecs_task_policy" {
  policy_arn = aws_iam_policy.statgpt2_ecs_task_policy.arn
  role       = aws_iam_role.statgpt2_ecs_task_role.name
}

resource "aws_wafv2_web_acl" "statgpt2_waf" {
  name        = "statgpt2_waf"
  scope       = "REGIONAL"
  default_action {
    allow {}
  }
  visibility_config {
    cloud_watch_metrics_enabled = true
    metric_name                = "statgpt2_waf"
    sampled_requests_enabled    = true
  }

  rule {
    name     = "RateLimitRule"
    priority = 1
    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloud_watch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled    = true
    }
  }

  tags = {
    Name        = "statgpt2_waf"
    Environment = var.environment
  }
}