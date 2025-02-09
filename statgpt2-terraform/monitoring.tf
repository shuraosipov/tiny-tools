resource "aws_cloudwatch_log_group" "statgpt2_log_group" {
  name              = "/statgpt2/logs"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    Project     = "StatGPT 2.0"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_alarm" {
  alarm_name          = "HighCPUAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/ECS"
  period             = "60"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "This alarm triggers when CPU utilization exceeds 80%."
  dimensions = {
    ClusterName = aws_ecs_cluster.statgpt2_cluster.name
    ServiceName = aws_ecs_service.statgpt2_service.name
  }

  alarm_actions = [aws_sns_topic.statgpt2_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "high_memory_alarm" {
  alarm_name          = "HighMemoryAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "MemoryUtilization"
  namespace          = "AWS/ECS"
  period             = "60"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "This alarm triggers when memory utilization exceeds 80%."
  dimensions = {
    ClusterName = aws_ecs_cluster.statgpt2_cluster.name
    ServiceName = aws_ecs_service.statgpt2_service.name
  }

  alarm_actions = [aws_sns_topic.statgpt2_alerts.arn]
}

resource "aws_sns_topic" "statgpt2_alerts" {
  name = "statgpt2-alerts"

  tags = {
    Environment = var.environment
    Project     = "StatGPT 2.0"
  }
}

resource "aws_cloudwatch_dashboard" "statgpt2_dashboard" {
  dashboard_name = "StatGPT2Dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric",
        x = 0,
        y = 0,
        width = 24,
        height = 6,
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.statgpt2_cluster.name, "ServiceName", aws_ecs_service.statgpt2_service.name],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.statgpt2_cluster.name, "ServiceName", aws_ecs_service.statgpt2_service.name]
          ],
          period = 300,
          stat = "Average",
          region = "us-east-1",
          title = "ECS Service Metrics"
        }
      }
    ]
  })
}