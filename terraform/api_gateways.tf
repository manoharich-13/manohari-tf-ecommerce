# Single API Gateway for all services
resource "aws_api_gateway_rest_api" "ecommerce_api" {
  name = "${var.project_prefix}-api"
}

# /products
resource "aws_api_gateway_resource" "products" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_rest_api.ecommerce_api.root_resource_id
  path_part   = "products"
}

resource "aws_api_gateway_method" "products_get" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.products.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "products_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.products.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "products_get" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.products.id
  http_method = aws_api_gateway_method.products_get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.product_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "products_options" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.products.id
  http_method = aws_api_gateway_method.products_options.http_method
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# /cart
resource "aws_api_gateway_resource" "cart" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_rest_api.ecommerce_api.root_resource_id
  path_part   = "cart"
}

resource "aws_api_gateway_method" "cart_post" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.cart.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "cart_get" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.cart.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "cart_delete" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.cart.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "cart_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.cart.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cart_post" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.cart.id
  http_method = aws_api_gateway_method.cart_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.cart_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "cart_get" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.cart.id
  http_method = aws_api_gateway_method.cart_get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.cart_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "cart_delete" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.cart.id
  http_method = aws_api_gateway_method.cart_delete.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.cart_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "cart_options" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.cart.id
  http_method = aws_api_gateway_method.cart_options.http_method
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# /pay
resource "aws_api_gateway_resource" "pay" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_rest_api.ecommerce_api.root_resource_id
  path_part   = "pay"
}

resource "aws_api_gateway_method" "pay_post" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.pay.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "pay_get" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.pay.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "pay_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.pay.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "pay_post" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.pay.id
  http_method = aws_api_gateway_method.pay_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.payment_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "pay_get" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.pay.id
  http_method = aws_api_gateway_method.pay_get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.payment_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "pay_options" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.pay.id
  http_method = aws_api_gateway_method.pay_options.http_method
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# CORS
resource "aws_api_gateway_method_response" "options_200" {
  for_each = {
    products = aws_api_gateway_resource.products.id
    cart = aws_api_gateway_resource.cart.id
    pay = aws_api_gateway_resource.pay.id
  }

  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin" = true
  }

  depends_on = [
    aws_api_gateway_method.products_options,
    aws_api_gateway_method.cart_options,
    aws_api_gateway_method.pay_options
  ]
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  for_each = {
    products = aws_api_gateway_resource.products.id
    cart = aws_api_gateway_resource.cart.id
    pay = aws_api_gateway_resource.pay.id
  }

  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS,DELETE'"
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [aws_api_gateway_method_response.options_200]
}

# Lambda Permissions
resource "aws_lambda_permission" "api_gateway_products" {
  statement_id = "AllowAPIGatewayInvokeProducts"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.product_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.ecommerce_api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "api_gateway_cart" {
  statement_id = "AllowAPIGatewayInvokeCart"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cart_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.ecommerce_api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "api_gateway_pay" {
  statement_id = "AllowAPIGatewayInvokePay"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.payment_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.ecommerce_api.execution_arn}/*/*/*"
}

# /auth
resource "aws_api_gateway_resource" "auth" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_rest_api.ecommerce_api.root_resource_id
  path_part   = "auth"
}

# /auth/register
resource "aws_api_gateway_resource" "auth_register" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "register"
}

resource "aws_api_gateway_method" "auth_register_post" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.auth_register.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "auth_register_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.auth_register.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "auth_register_post" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_register.id
  http_method = aws_api_gateway_method.auth_register_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.auth_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "auth_register_options" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_register.id
  http_method = aws_api_gateway_method.auth_register_options.http_method
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# /auth/login
resource "aws_api_gateway_resource" "auth_login" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "login"
}

resource "aws_api_gateway_method" "auth_login_post" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.auth_login.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "auth_login_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.auth_login.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "auth_login_post" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.auth_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "auth_login_options" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login_options.http_method
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "auth_login_post_200" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = "POST"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "auth_login_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = "POST"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# CORS for Auth
resource "aws_api_gateway_method_response" "auth_register_options_200" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_register.id
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "auth_register_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_register.id
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [
    aws_api_gateway_method_response.auth_register_options_200,
    aws_api_gateway_integration.auth_register_options
  ]
}

resource "aws_api_gateway_method_response" "auth_login_options_200" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "auth_login_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = "OPTIONS"
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [
    aws_api_gateway_method_response.auth_login_options_200,
    aws_api_gateway_integration.auth_login_options
  ]
}

# Lambda Permissions for Auth
resource "aws_lambda_permission" "api_gateway_auth" {
  statement_id = "AllowAPIGatewayInvokeAuth"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.ecommerce_api.execution_arn}/*/*/*"
}

# Deployment
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.products_get,
    aws_api_gateway_integration.cart_post,
    aws_api_gateway_integration.cart_get,
    aws_api_gateway_integration.cart_delete,
    aws_api_gateway_integration.pay_post,
    aws_api_gateway_integration.pay_get,
    aws_api_gateway_integration.auth_register_post,
    aws_api_gateway_integration.auth_register_options,
    aws_api_gateway_integration.auth_login_post,
    aws_api_gateway_integration.auth_login_options
  ]

  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.products.id,
      aws_api_gateway_resource.cart.id,
      aws_api_gateway_resource.pay.id,
      aws_api_gateway_resource.auth.id,
      aws_api_gateway_resource.auth_register.id,
      aws_api_gateway_resource.auth_login.id,
      aws_lambda_function.product_lambda.id,
      aws_lambda_function.cart_lambda.id,
      aws_lambda_function.payment_lambda.id,
      aws_lambda_function.auth_lambda.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Stage
resource "aws_api_gateway_stage" "dev" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  stage_name    = "dev"
}

