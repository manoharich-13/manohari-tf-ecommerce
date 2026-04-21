# Ecommerce System

A serverless e-commerce application built with AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **Frontend**: HTML/CSS/JavaScript with API versioning support via headers
- **Backend**: AWS Lambda functions for products, cart, and payment services
- **Database**: DynamoDB tables for products, cart, and payments
- **API**: API Gateway with REST endpoints using header-based versioning

                   ┌──────────────────────────────┐
                   │           USER               │
                   │        (Browser UI)          │
                   └─────────────┬────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │                FRONTEND                    │
        │  HTML / CSS / JavaScript                  │
        │  - Version selector (v1 / v2)             │
        │  - Sends Api-Version header              │
        └─────────────┬────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────────────────────┐
        │              API GATEWAY                   │
        │  - REST Endpoints                         │
        │  - Reads "Api-Version" header            │
        │  - Routes to appropriate Lambda logic    │
        └───────┬──────────────┬──────────────┬─────┘
                │              │              │
                ▼              ▼              ▼

   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
   │ PRODUCT SERVICE│  │  CART SERVICE  │  │ PAYMENT SERVICE│
   │   (Lambda)     │  │   (Lambda)     │  │   (Lambda)     │
   │                │  │                │  │                │
   │ GET /products  │  │ POST /cart     │  │ POST /pay      │
   │ (v1 / v2 logic)│  │ GET /cart      │  │ GET /pay       │
   └──────┬─────────┘  └──────┬─────────┘  └──────┬─────────┘
          │                   │                   │
          ▼                   ▼                   ▼

 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ DynamoDB       │  │ DynamoDB       │  │ DynamoDB       │
 │ Products Table │  │ Cart Table     │  │ Payments Table │
 └────────────────┘  └────────────────┘  └────────────────┘


                ┌──────────────────────────────────────┐
                │        TERRAFORM (IaC Layer)         │
                │--------------------------------------│
                │ - API Gateway                        │
                │ - Lambda Functions                   │
                │ - DynamoDB Tables                    │
                │ - IAM Roles & Permissions            │
                │ - Deployment Automation              │
                └──────────────────────────────────────┘
## API Endpoints

### Products
- `GET /products` - List all products (use `Api-Version: v1` or `v2` header)

### Cart
- `POST /cart` - Add item to cart
- `GET /cart?userId={id}` - Get cart items
- `DELETE /cart?userId={id}&itemId={id}` - Remove item from cart
- All cart endpoints accept `Api-Version` header

### Payment
- `POST /pay` - Process payment
- `GET /pay` - Get payment history
- Accepts `Api-Version` header

## API Versioning

This application demonstrates **header-based API versioning**. Instead of using URL paths like `/v1/products`, versioning is handled through the `Api-Version` header:

```
GET /products
Api-Version: v1
```

The frontend includes version selectors that set the appropriate header for API requests.

## Setup

1. Install Terraform
2. Configure AWS credentials
3. Run `terraform init`
4. Run `terraform plan`
5. Run `terraform apply`
6. Open `manohari-tf-index.html` in a browser

## Testing

Run unit tests:
```bash
python -m pytest manohari-tf-tests/unit/
```

## Versioning Implementation

- **Header-based**: Uses `Api-Version` header instead of URL paths
- **Backward compatible**: Same endpoints, different behavior based on header
- **Frontend control**: Users can select API version via dropdown
