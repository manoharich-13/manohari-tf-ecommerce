# DynamoDB Tables

data "aws_dynamodb_table" "products" {
  name = "Products_M"
}

data "aws_dynamodb_table" "cart" {
  name = "Cart_M"
}

resource "aws_dynamodb_table" "payments" {
  name         = "payments-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "payment_id"

  attribute {
    name = "payment_id"
    type = "S"
  }

  tags = {
    Name = "Payments"
  }
}

# Users Table for Authentication
resource "aws_dynamodb_table" "users" {
  name         = "users-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }

  tags = {
    Name = "Users"
  }
}

# Sample Products
resource "aws_dynamodb_table_item" "product1" {
  table_name = data.aws_dynamodb_table.products.name
  hash_key   = data.aws_dynamodb_table.products.hash_key

  item = jsonencode({
    id            = { S = "p1" }
    product_name  = { S = "iPhone 15" }
    price         = { N = "79999" }
    availability  = { N = "50" }
    rating        = { N = "4.8" }
  })
}

resource "aws_dynamodb_table_item" "product2" {
  table_name = data.aws_dynamodb_table.products.name
  hash_key   = data.aws_dynamodb_table.products.hash_key

  item = jsonencode({
    id            = { S = "p2" }
    product_name  = { S = "MacBook Air" }
    price         = { N = "99999" }
    availability  = { N = "30" }
    rating        = { N = "4.9" }
  })
}

resource "aws_dynamodb_table_item" "product3" {
  table_name = data.aws_dynamodb_table.products.name
  hash_key   = data.aws_dynamodb_table.products.hash_key

  item = jsonencode({
    id            = { S = "p3" }
    product_name  = { S = "AirPods Pro" }
    price         = { N = "24999" }
    availability  = { N = "100" }
    rating        = { N = "4.7" }
  })
}

# Sample Cart Items (for user1)
resource "aws_dynamodb_table_item" "cart_sample1" {
  table_name = data.aws_dynamodb_table.cart.name
  hash_key   = data.aws_dynamodb_table.cart.hash_key
  range_key  = data.aws_dynamodb_table.cart.range_key

  item = jsonencode({
    userId        = { S = "user1" }
    itemId        = { S = "p1" }
    product_name  = { S = "iPhone 15" }
    price         = { N = "79999" }
    quantity      = { N = "1" }
    total_price   = { N = "79999" }
  })
}

# Sample Payment Item
resource "aws_dynamodb_table_item" "payment_sample1" {
  table_name = aws_dynamodb_table.payments.name
  hash_key   = aws_dynamodb_table.payments.hash_key

  item = jsonencode({
    payment_id = { S = "pay1" }
    amount     = { N = "500" }
    user       = { S = "user1" }
  })
}

