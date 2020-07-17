output "aws_ecs_task_definition" {
  value = aws_ecs_task_definition.web.arn
}

output "aws_ecs_service" {
  value = aws_ecs_service.web.id
}

