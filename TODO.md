# Ecommerce System Deployment TODO

## Phase 1: Infrastructure Setup (Terraform)
- [x] Split `main.tf` into modular files: `dynamodb.tf`, `lambdas.tf`, `api_gateways.tf`
- [x] Add DynamoDB tables: Products_M, Cart_M with sample data
- [x] Add IAM roles/policies for all Lambdas
- [x] Define all Lambdas (product, cart, payment) with archive_file zips
- [x] Create single API Gateway with routes: /products (GET), /cart (POST/GET/DELETE), /pay (POST/GET)
- [x] Add CORS and Lambda permissions
- [x] Update variables.tf, outputs.tf with all endpoints
- [x] Run `terraform init && terraform plan`

## Phase 2: Code Fixes
- [x] Fix service .py handlers, DynamoDB table names consistency
- [x] Update index.html with new API Gateway URL from outputs

## Phase 3: Testing & Deploy
- [x] `terraform apply`
- [x] Update frontend APIs
- [x] Run pytest
- [ ] Test end-to-end via index.html

## Phase 4: Documentation
- [x] README.md with setup/run instructions
- [ ] Test end-to-end via index.html

