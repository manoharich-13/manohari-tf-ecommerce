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
