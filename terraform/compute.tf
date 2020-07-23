# Cloudwatch Logs
resource "aws_cloudwatch_log_group" "web" {
  name = "ecs-service-logs/its-${var.environment}-web"
}

# ECS task and service

resource "aws_ecs_task_definition" "web" {
  family                = "its-web"
  task_role_arn         = aws_iam_role.its_task.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.its_task.arn
  cpu                      = var.cpu
  memory                   = var.memory

  container_definitions = <<DEFINITION
[
  {
    "name": "web",
    "image": "${aws_ecr_repository.its_ecr.repository_url}",
    "cpu": ${var.cpu},
    "memory": ${var.memory},
    "essential": true,
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.web.name}",
          "awslogs-region": "${var.aws_region}",
          "awslogs-stream-prefix": "ecs"
        }
    },
    "environment": [
      {"name": "PARAMETER_PATH", "value" : "${var.parameter_path}"}
   ],
   "portMappings": [
      {
        "containerPort": 5000
      }
   ],
    "entryPoint": ["./scripts/docker/server/run-server.sh"]
  }
]
DEFINITION
  tags = {
    Name        = "its-${var.environment}"
    Environment = var.environment
    Creator     = "Terraform"
  }

}

resource "aws_ecs_service" "web" {
  name            = "its_${var.environment}_web_service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.web.arn
  launch_type     = var.fargate_spot_capacity_provider == "yes" ? null : "FARGATE"

  desired_count = var.desired_count

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50

  load_balancer {
    target_group_arn = aws_alb_target_group.its.arn
    container_name   = "web"
    container_port   = 5000
  }

  network_configuration {
    security_groups = [var.its_sg]
    subnets         = var.private_subnets
  }

  # ignore changes to desired count so that deployments won't reset us to our minimum
  lifecycle {
    ignore_changes = [desired_count, task_definition]
  }

  dynamic "capacity_provider_strategy" {
    for_each = var.fargate_spot_capacity_provider == "no" ? [] : [1]
    content {
      capacity_provider = var.capacity_provider_1
      weight            = 1
    }
  }
  dynamic "capacity_provider_strategy" {
    for_each = var.fargate_capacity_provider == "no" ? [] : [1]
    content {
      capacity_provider = var.capacity_provider_2
      weight            = 1
    }
  }
}

# Application Auto Scaling

resource "aws_appautoscaling_target" "web" {
  resource_id        = "service/${var.ecs_cluster_name}/${aws_ecs_service.web.name}"
  role_arn           = var.ecs_service_autoscale_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  min_capacity       = var.min_capacity
  max_capacity       = var.container_scaling_limit
}

resource "aws_appautoscaling_policy" "its_web_scale_up" {
  name               = "its-${var.environment}-web-scale-up"
  resource_id        = "service/${var.ecs_cluster_name}/${aws_ecs_service.web.name}"
  scalable_dimension = "ecs:service:DesiredCount"

  service_namespace = "ecs"

  # plus eight every time we scale up, cooldown two minutes
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 120
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = 8
    }
  }

  depends_on = [aws_appautoscaling_target.web]
}

resource "aws_appautoscaling_policy" "its_web_scale_down" {
  name               = "its-${var.environment}-web-scale-down"
  resource_id        = "service/${var.ecs_cluster_name}/${aws_ecs_service.web.name}"
  scalable_dimension = "ecs:service:DesiredCount"

  service_namespace = "ecs"

  # scale down slowly - one at a time, cooldown two minutes
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 120
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }

  depends_on = [aws_appautoscaling_target.web]
}

resource "aws_cloudwatch_metric_alarm" "its_web_requests_high" {
  alarm_name          = "its-${var.environment}-web-RequestCountPerTarget-high"
  alarm_description   = "Scales up app containers based on RequestCountPerTarget metric"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "RequestCountPerTarget"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "30"
  alarm_actions       = [aws_appautoscaling_policy.its_web_scale_up.arn]

  dimensions = {
    "TargetGroup"  = "${replace("${aws_alb_target_group.its.arn}", "/arn:.*?:targetgroup\\/(.*)/", "targetgroup/$1")}"
    "LoadBalancer" = "${replace("${aws_alb.its.arn}", "/arn:.*?:loadbalancer\\/(.*)/", "$1")}"
  }
}

resource "aws_cloudwatch_metric_alarm" "its_web_requests_low" {
  alarm_name          = "its-${var.environment}-web-RequestCountPerTarget-low"
  alarm_description   = "Scales down app containers based on RequestCountPerTarget metric"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "RequestCountPerTarget"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "15"
  alarm_actions       = [aws_appautoscaling_policy.its_web_scale_down.arn]

  dimensions = {
    "TargetGroup"  = "${replace("${aws_alb_target_group.its.arn}", "/arn:.*?:targetgroup\\/(.*)/", "targetgroup/$1")}"
    "LoadBalancer" = "${replace("${aws_alb.its.arn}", "/arn:.*?:loadbalancer\\/(.*)/", "$1")}"
  }
}

