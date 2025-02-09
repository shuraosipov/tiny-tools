# StatGPT 2.0 Terraform Infrastructure

This repository contains the Terraform configuration for deploying the StatGPT 2.0 statistical data platform on AWS. The infrastructure is designed to be production-ready, secure, and scalable, leveraging various AWS services to process statistical data using AI/ML capabilities and serve it through a REST API.

## Project Structure

- **main.tf**: Main Terraform configuration, including provider setup and resource tagging.
- **variables.tf**: Definitions of all variables used throughout the configuration.
- **networking.tf**: VPC and subnet configurations for network isolation and connectivity.
- **compute.tf**: ECS cluster and related resources for container orchestration.
- **database.tf**: RDS and OpenSearch configurations for data storage and indexing.
- **security.tf**: Security groups, IAM roles, and WAF rules for API protection.
- **monitoring.tf**: CloudWatch configurations for logging and monitoring.
- **cdn.tf**: CloudFront distribution for global content delivery.
- **README.md**: Documentation for setup and usage.

## Getting Started

### Prerequisites

- Terraform installed on your local machine.
- AWS account with appropriate permissions to create resources.
- AWS CLI configured with your credentials.

### Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd statgpt2-terraform
   ```

2. Initialize Terraform:
   ```
   terraform init
   ```

3. Review and customize the `variables.tf` file to set your desired configurations.

4. Plan the deployment:
   ```
   terraform plan
   ```

5. Apply the configuration to create the infrastructure:
   ```
   terraform apply
   ```

6. Monitor the deployment process and verify that all resources are created successfully.

## Usage Guidelines

- Ensure that you have the necessary IAM permissions to manage the resources defined in the Terraform configuration.
- Regularly review and update the configurations as needed to adapt to changing requirements or AWS best practices.
- Use the `terraform destroy` command to remove all resources when they are no longer needed.

## Overview of Infrastructure Components

- **VPC**: A dedicated Virtual Private Cloud with public and private subnets for secure network isolation.
- **ECS**: Container orchestration service for running the application in a scalable manner.
- **RDS**: Managed relational database service for storing metadata securely.
- **OpenSearch**: Search and analytics engine for indexing and querying statistical data.
- **Redis**: In-memory data structure store for caching and improving performance.
- **S3**: Object storage service for storing datasets.
- **CloudFront**: Content delivery network for optimizing the delivery of content globally.
- **CloudWatch**: Monitoring and logging service for tracking performance and auditing.

## Security Considerations

- All data is encrypted at rest and in transit.
- IAM roles are configured with least privilege access.
- WAF rules are implemented to protect the API from common web exploits.
- Regular automated backups are scheduled for critical data.

For more detailed information on each component, please refer to the respective Terraform files in this repository.