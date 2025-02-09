resource "aws_ecs_cluster" "statgpt2_cluster" {
  name = "${var.environment}-statgpt2-cluster"
}

resource "aws_ecs_task_definition" "statgpt2_task" {
  family                   = "${var.environment}-statgpt2-task"
  network_mode             = "awsvpc"
  requires_compatibilities  = ["FARGATE"]
  cpu                      = "2048"  # 2 vCPU
  memory                   = "4096"  # 4 GB

  container_definitions = jsonencode([
    {
      name      = "statgpt2-container"
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = 443
          hostPort      = 443
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "DATABASE_URL"
          value = aws_rds_instance.statgpt2_db.endpoint
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "statgpt2_service" {
  name            = "${var.environment}-statgpt2-service"
  cluster         = aws_ecs_cluster.statgpt2_cluster.id
  task_definition = aws_ecs_task_definition.statgpt2_task.arn
  desired_count   = 2  # Adjust based on load
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.statgpt2_target_group.arn
    container_name   = "statgpt2-container"
    container_port   = 443
  }

  depends_on = [aws_lb_listener.statgpt2_listener]
}

resource "aws_appautoscaling_target" "statgpt2_autoscale_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.statgpt2_cluster.name}/${aws_ecs_service.statgpt2_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "statgpt2_scale_out" {
  name                   = "${var.environment}-scale-out"
  policy_type           = "StepScaling"
  resource_id           = aws_appautoscaling_target.statgpt2_autoscale_target.id
  scalable_dimension     = aws_appautoscaling_target.statgpt2_autoscale_target.scalable_dimension
  service_namespace      = aws_appautoscaling_target.statgpt2_autoscale_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type = "ChangeInCapacity"
    step_adjustment {
      scaling_adjustment = 1
      metric_interval_lower_bound = 0
    }
    cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "statgpt2_scale_in" {
  name                   = "${var.environment}-scale-in"
  policy_type           = "StepScaling"
  resource_id           = aws_appautoscaling_target.statgpt2_autoscale_target.id
  scalable_dimension     = aws_appautoscaling_target.statgpt2_autoscale_target.scalable_dimension
  service_namespace      = aws_appautoscaling_target.statgpt2_autoscale_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type = "ChangeInCapacity"
    step_adjustment {
      scaling_adjustment = -1
      metric_interval_upper_bound = 0
    }
    cooldown = 60
  }
}