resource "aws_alb_target_group" "its" {
  name     = "its-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"

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
  name     = "its-fallback-fargate-${var.environment}"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"


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


resource "aws_security_group_rule" "its_sg_outbound_internet_access" {
  description       = "allow all outound connections for its-${var.environment}"
  type              = "egress"
  protocol          = "-1"
  from_port         = 0
  to_port           = 0
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = var.its_sg
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

############################################################################
# Route53 DNS
############################################################################

locals {
  its_dns = "its.${var.route53_zone_name}"
}
locals {
  its_cdn_dns = "image.${var.route53_zone_name}"
}

resource "aws_route53_record" "its_dns" {
  zone_id = var.route53_zone
  name    = local.its_dns
  type    = "CNAME"
  ttl     = "60"
  records = [ aws_alb.its.dns_name ]
}

resource "aws_route53_record" "its_cloudfront_dns" {
  zone_id  = var.route53_zone
  name     = local.its_cdn_dns
  type     = "CNAME"
  ttl      = "300"
  records  = [aws_cloudfront_distribution.its_cloudfront_distribution.domain_name]
}
############################################################################
# Cloudfront Distribution
############################################################################

locals {
  aws_cloudfront_distribution_origin_id = "alb-its-${var.environment}"
}

resource "aws_cloudfront_distribution" "its_cloudfront_distribution" {

  origin {
    domain_name = aws_alb.its.dns_name
    origin_id   = local.aws_cloudfront_distribution_origin_id

  custom_origin_config {
    http_port = 80
    https_port = 443
    origin_keepalive_timeout = 5
    origin_protocol_policy = "http-only"
    origin_read_timeout = 30
    origin_ssl_protocols = ["TLSv1", "TLSv1.1", "TLSv1.2"]
  }
}

  enabled         = true
  price_class     = "PriceClass_100"
  is_ipv6_enabled = true

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    acm_certificate_arn      = var.ssl_cert_arn
    minimum_protocol_version = "TLSv1.2_2018"
    ssl_support_method       = "sni-only"
  }

  aliases = [local.its_cdn_dns, local.its_dns]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.aws_cloudfront_distribution_origin_id
    default_ttl      = 0
    compress         = true
    
    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
      headers = var.cdn_headers
      
    }

    viewer_protocol_policy = "allow-all"
  }
}