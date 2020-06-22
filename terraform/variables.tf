variable "vpc_id" {
  type        = string
  description = "id of the Virtual Private Cloud network in which to create resources"
}

variable "environment" {
  type        = string
  description = "tag for environment, such as prod, staging or qa"
}

variable "s3_buckets" {
  type        = list
  description = "names for the S3 buckets ITS will use to store images"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "the name of the AWS region in which to create resources"
}

variable "ssl_cert_arn" {
  type        = string
  description = "Amazon Resource Name for the ssl cert on the ITS load balancer"
}

variable "ecs_cluster_name" {
  type        = string
  description = "name of ECS cluster in which to run containers"
}

variable "ecs_cluster_id" {
  type        = string
  description = "id of ECS cluster in which to run containers"
}

variable "allowed_host" {
  type        = string
  description = "hostname for incoming web traffic"
}

variable "parameter_store_path_arn" {
  type        = string
  description = "Amazon Resource Name for parameter store path (where the application will look for configuration)"
}

variable "ecs_service_autoscale_role_arn" {
  type        = string
  description = "Amazon Resource Name for the IAM role ECS should use when autoscaling"
}

variable "vpc_subnet_ids" {
  type        = list
  description = "ids of subnets to which the load balancer should be attached"
}

variable "its_sg" {
  type        = string
  description = "security group id for ECS cluster instances"
}

variable "container_scaling_limit" {
  default     = 8
  description = "limit to the autoscaling behavior of the ECS service"
}

variable "private_subnets" {
  type        = list
  description = "ids of subnets to which the load balancer should be attached"
}

variable "cluster_name" {
}

variable "cluster_arn" {
}


