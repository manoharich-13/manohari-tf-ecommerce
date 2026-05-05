# Lambda IAM Role (shared for all services)
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "dynamo_full" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# ---------------- PRODUCT ----------------
data "archive_file" "product_zip" {
  type        = "zip"
  source_file = "../backend/manohari_tf_product_service/product_service.py"
  output_path = "product_service.zip"
}

resource "aws_lambda_function" "product_lambda" {
  function_name = "${var.project_prefix}-product-service"
  role          = aws_iam_role.lambda_role.arn
  handler       = "product_service.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.product_zip.output_path
  source_code_hash = data.archive_file.product_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = data.aws_dynamodb_table.products.name
    }
  }
}

# ---------------- CART ----------------
data "archive_file" "cart_zip" {
  type        = "zip"
  source_file = "../backend/manohari_tf_cart_service/cart_lambda.py"
  output_path = "cart_service.zip"
}

resource "aws_lambda_function" "cart_lambda" {
  function_name = "${var.project_prefix}-cart-service"
  role          = aws_iam_role.lambda_role.arn
  handler       = "cart_lambda.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.cart_zip.output_path
  source_code_hash = data.archive_file.cart_zip.output_base64sha256

  environment {
    variables = {
      PRODUCTS_TABLE = data.aws_dynamodb_table.products.name
      CART_TABLE     = data.aws_dynamodb_table.cart.name
    }
  }
}

# ---------------- PAYMENT ----------------
data "archive_file" "payment_zip" {
  type        = "zip"
  source_file = "../backend/manohari_tf_payment_service/payment.py"
  output_path = "payment_service.zip"
}

resource "aws_lambda_function" "payment_lambda" {
  function_name = "${var.project_prefix}-payment-service"
  role          = aws_iam_role.lambda_role.arn
  handler       = "payment.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.payment_zip.output_path
  source_code_hash = data.archive_file.payment_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.payments.name
    }
  }
}

# ---------------- AUTH ----------------
data "archive_file" "auth_zip" {
  type        = "zip"
  source_file = "../backend/manohari_tf_auth_service/auth_service.py"
  output_path = "auth_service.zip"
}

resource "aws_lambda_function" "auth_lambda" {
  function_name = "${var.project_prefix}-auth-service"
  role          = aws_iam_role.lambda_role.arn
  handler       = "auth_service.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.auth_zip.output_path
  source_code_hash = data.archive_file.auth_zip.output_base64sha256

  environment {
    variables = {
      USERS_TABLE = aws_dynamodb_table.users.name
    }
  }
}