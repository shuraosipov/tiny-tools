resource "aws_db_instance" "statgpt2_rds" {
  identifier              = "statgpt2-rds"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.large"
  allocated_storage       = 20
  storage_type           = "gp2"
  multi_az               = true
  username               = var.db_username
  password               = var.db_password
  db_name                = var.db_name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true

  tags = {
    Name        = "StatGPT2 RDS"
    Environment = var.environment
  }
}

resource "aws_opensearch_domain" "statgpt2_opensearch" {
  domain_name = "statgpt2-opensearch"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "t3.medium.search"
    instance_count = 2
    dedicated_master_enabled = true
    dedicated_master_type = "t3.medium.search"
    dedicated_master_count = 3
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 20
    volume_type = "gp2"
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "es:*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "StatGPT2 OpenSearch"
    Environment = var.environment
  }
}