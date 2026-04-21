# Ecommerce Infrastructure
# All resources now in modular files:
# - dynamodb.tf : DynamoDB tables for Products_M, Cart_M, payments-table with sample data
# - lambdas.tf : Product, Cart, Payment Lambdas with zips from service dirs
# - api_gateways.tf : Single unified API Gateway ecommerce-api with routes /products /cart /pay
# - variables.tf / outputs.tf / provider.tf supporting
#
# Deploy with: terraform plan && terraform apply
#
# Frontend: index.html calls the new endpoints (update URLs from terraform output api_base_url after deploy)

