resource "aws_alb_target_group" "its" {
  name     = "its-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  # controls how long load balancer holds onto obsolete containers before closing their connections -
  # shortening this tends to shorten deployment time. default is 300 seconds.
  deregistration_delay = 150

  health_check {
    healthy_threshold   = 5
    unhealthy_threshold = 2
    timeout             = 5
    path                = "/"
    protocol            = "HTTP"
    interval            = 30
    matcher             = "200,400,404"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_alb.its]
}

# this is just a fairly low-level way to foil the dumber port-scanners - if the connect without the right host header,
# we send them to a target group with nothing listening, so they get a 503 or similar
resource "aws_alb_target_group" "fallback" {
  name     = "its-fallback-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_alb.its]
}

resource "aws_security_group" "its_lb" {
  description = "controls access to the ${var.environment} its load balancer"

  vpc_id = var.vpc_id
  name   = "its-${var.environment}-lb-sg"

  # allow public HTTP ingress
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  # allow public HTTPS ingress
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  # send any traffic anywhere
  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
}

# allow all traffic from the its load balancer to the ECS cluster machines
resource "aws_security_group_rule" "its_lb_to_cluster" {
  type     = "ingress"
  protocol = "tcp"

  from_port = 80
  to_port   = 65535

  source_security_group_id = aws_security_group.its_lb.id
  security_group_id        = var.its_sg
}

resource "aws_alb" "its" {
  name            = "its-${var.environment}"
  subnets         = var.vpc_subnet_ids
  security_groups = [aws_security_group.its_lb.id]
}

resource "aws_alb_listener" "its_http" {
  load_balancer_arn = aws_alb.its.id
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.fallback.id
    type             = "forward"
  }
}

resource "aws_alb_listener" "its_https" {
  load_balancer_arn = aws_alb.its.id
  port              = "443"
  protocol          = "HTTPS"

  # "recommended for general use" as of 2017-10-19
  # http://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html#describe-ssl-policies
  ssl_policy = "ELBSecurityPolicy-2016-08"

  certificate_arn = var.ssl_cert_arn

  default_action {
    target_group_arn = aws_alb_target_group.fallback.id
    type             = "forward"
  }
}

resource "aws_alb_listener_rule" "its_https" {
  listener_arn = aws_alb_listener.its_https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.its.arn
  }

  condition {
    field = "host-header"

    values = [var.allowed_host]
  }
}

resource "aws_alb_listener_rule" "its_http" {
  listener_arn = aws_alb_listener.its_http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.its.arn
  }

  condition {
    field = "host-header"

    values = [var.allowed_host]
  }
}

