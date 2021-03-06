# Configure the AWS Provider
provider "aws" {
  version = "~> 2.0"
  region  = "eu-west-1"
  profile = "d2si"
}
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../lambda"
  output_path = "../lambda_tgw_routetable.zip"
}

resource "aws_iam_role" "role_for_lambda" {
  name              = "role_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_tgw_routetable" {
  name          = "Policy4Lambdatgw_routetable"
  description   = "Policy for the lambda to get content of TGW route table"

  policy        = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ManageOwnAccessKeys",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeTransitGatewayRouteTables",
                "ec2:ExportTransitGatewayRoutes",
                "ec2:ExportTransitGatewayRoutes",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:CreateBucket",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:DeleteBucket",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "dynamodb:PutItem"
            ],
        "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_tgw_routetable" {
  role              = aws_iam_role.role_for_lambda.name
  policy_arn        = aws_iam_policy.lambda_tgw_routetable.arn
}

resource "aws_lambda_function" "lambda_tgw_routetable" {
  filename          = "../lambda_tgw_routetable.zip"
  function_name     = "Dev-TGWAutom-ListRouteTable"
  role              = aws_iam_role.role_for_lambda.arn
  handler           = "lambda_tgw.lambda_handler"
  source_code_hash  = "$data.archive_file.lambda_log_parser-zip.output_base64sha256"
  runtime           = "python3.7"
  memory_size       = "1024"
  timeout           = "60"
  publish           = "false"

  }

resource "aws_cloudwatch_event_rule" "check_tgw_routetable" {
  name                = "CloudWatch-tgw_routetable"
  description         = "Every Month Cron to check TGW Route Table"
  schedule_expression = "cron(0 0 1 * ? *)"
}

resource "aws_dynamodb_table" "dynamodb-table" {
  name           = "TGW"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  attribute {
    name = "Id"
    type = "S"
  }
}
# resource "aws_cloudwatch_event_target" "lambda_target" {
#   rule      = "${aws_cloudwatch_event_rule.watch_creds.name}"
#   arn       = "${aws_lambda_alias.alias_dev.arn}"
# }

# resource "aws_ses_email_identity" "example" {
#   email = "pierre.poree@d2si.io"
# }


# resource "aws_lambda_alias" "alias_prod" {
#   name             = "Prod"
#   description      = "Alias for the Prod"
#   function_name    = "${aws_lambda_function.lambda_tgw_routetable.arn}"
#   function_version = "$LATEST"

  # A map that defines the proportion of events 
  # that should be sent to different versions of a lambda function.
  # routing_config {
  #   additional_version_weights = {
  #     "2" = 0.1 # 10% of requests sent to lambda version 2
  #    }
  # }

# }

# resource "aws_lambda_alias" "alias_dev" {
#   name             = "Dev"
#   description      = "Alias for the Dev"
#   function_name    = "${aws_lambda_function.lambda_tgw_routetable.arn}"
#   function_version = "$LATEST"
# }              