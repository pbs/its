# Cloudwatch Logs
resource "aws_cloudwatch_log_group" "web" {
  name = "ecs-service-logs/its-${var.environment}-web"
}

# ECS task and service
data "template_file" "web_task_def" {
  template = file("${path.module}/web-task-definition.json")

  vars = {
    log_group_region = var.aws_region
    log_group_name   = aws_cloudwatch_log_group.web.name
    hostname         = "its-${var.environment}"
    image_repo       = aws_ecr_repository.its_ecr.repository_url
    parameter_path = join(
      "",
      slice(split("parameter", var.parameter_store_path_arn), 1, 2),
    )
  }
}

resource "aws_ecs_task_definition" "web" {
  family                = "its-web"
  task_role_arn         = aws_iam_role.its_task.arn
  container_definitions = data.template_file.web_task_def.rendered
}

resource "aws_ecs_service" "web" {
  name            = "its_${var.environment}_web_service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.web.arn
  launch_type     = "FARGATE"


  desired_count = 2

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50

  load_balancer {
    target_group_arn = aws_alb_target_group.its.arn
    container_name   = "its-${var.environment}"
    container_port   = 5000
  }

  network_configuration {
    security_groups = [var.its_sg]
    subnets         = var.private_subnets
  }

  # ignore changes to desired count so that deployments won't reset us to our minimum
  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Application Auto Scaling

resource "aws_appautoscaling_target" "web" {
  resource_id        = "service/${var.ecs_cluster_name}/${aws_ecs_service.web.name}"
  role_arn           = var.ecs_service_autoscale_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  min_capacity       = 2
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
    metric_aggregation_type = "Average"

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
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }

  depends_on = [aws_appautoscaling_target.web]
}

# these two alarms are essentially an OR for scaling up - either will trigger scaling
resource "aws_cloudwatch_metric_alarm" "its_web_cpu_high" {
  alarm_name          = "its-${var.environment}-web-cpu-utilization-high"
  alarm_description   = "This alarm monitors its web CPU utilization for scaling up"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "4"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_appautoscaling_policy.its_web_scale_up.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = aws_ecs_service.web.name
  }
}

resource "aws_cloudwatch_metric_alarm" "its_web_memory_high" {
  alarm_name          = "its-${var.environment}-web-memory-utilization-high"
  alarm_description   = "This alarm monitors its web memory utilization for scaling up"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "4"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_appautoscaling_policy.its_web_scale_up.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = aws_ecs_service.web.name
  }
}

# scale down alarms - you can't AND on cloudwatch metrics / app autoscaling,
# so we have to pick one. low cpu seems like a reasonable flag

resource "aws_cloudwatch_metric_alarm" "its_web_cpu_low" {
  alarm_name          = "its-${var.environment}-web-cpu-utilization-low"
  alarm_description   = "This alarm monitors its web CPU utilization for scaling down"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "5"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "30"
  alarm_actions       = [aws_appautoscaling_policy.its_web_scale_down.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = aws_ecs_service.web.name
  }
}

