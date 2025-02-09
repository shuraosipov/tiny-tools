variable "region" {
  description = "The AWS region to deploy the infrastructure"
  default     = "us-east-1"
}

variable "environment" {
  description = "The environment for the deployment (e.g., production, staging)"
  default     = "production"
}

variable "ecs_instance_type" {
  description = "EC2 instance type for ECS tasks"
  default     = "t3.large"
}

variable "rds_instance_type" {
  description = "RDS instance type for MySQL database"
  default     = "db.t3.medium"
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  default     = "t3.medium.search"
}

variable "redis_instance_type" {
  description = "Redis instance type"
  default     = "cache.t3.medium"
}

variable "db_username" {
  description = "The username for the RDS database"
  type        = string
}

variable "db_password" {
  description = "The password for the RDS database"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "The name of the RDS database"
  default     = "statgpt2_db"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  type        = string
}

variable "waf_web_acl_id" {
  description = "WAF Web ACL ID for API protection"
  type        = string
}

variable "cloudfront_certificate_arn" {
  description = "ARN of the SSL certificate for CloudFront"
  type        = string
}