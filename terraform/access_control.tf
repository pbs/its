resource "aws_iam_role" "its_task" {
  name = "its-${var.environment}-app-ecs"

  assume_role_policy = <<EOF
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Sid": ""
    }
  ],
  "Version": "2008-10-17"
}
EOF

}

# putMetricData permissions to * is dumb, but according to AWS docs it's not
# possible to limit it further:
# > CloudWatch does not have any resources for you to control using policies
#   resources, so use the wildcard character (*) in IAM policies.
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/iam-access-control-overview-cw.html
resource "aws_iam_role_policy" "its" {
  name = "its-${var.environment}-app-policy"
  role = aws_iam_role.its_task.name

  policy = <<EOF
{
    "Statement": [
        {
            "Action": [
                "cloudwatch:PutMetricData",
                "kms:ListKeys",
                "ssm:DescribeParameters"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Action": [
                "kms:Decrypt",
                "ssm:GetParametersByPath",
                "ssm:GetParameters"
            ],
            "Effect": "Allow",
            "Resource": "${var.parameter_store_path_arn}"
        }
    ],
    "Version": "2012-10-17"
}
EOF

}

resource "aws_iam_role_policy" "its-s3" {
  count = length(var.s3_buckets)
  name  = "its-${var.environment}-s3-policy-${count.index}"
  role  = aws_iam_role.its_task.name

  policy = <<EOF
{
    "Statement": [
        {
            "Action": [
              "s3:Get*"
            ],
            "Effect": "Allow",
            "Resource": [
              "arn:aws:s3:::${var.s3_buckets[count.index]}/*"
            ]
        },
        {
            "Action": [
              "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": [
              "arn:aws:s3:::${var.s3_buckets[count.index]}"
            ]
        }
    ],
    "Version": "2012-10-17"
}
EOF

}

