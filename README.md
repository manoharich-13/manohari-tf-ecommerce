# Ecommerce System

A serverless e-commerce application built with AWS Lambda, API Gateway, and DynamoDB, featuring user authentication.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │───▶│ API Gateway │───▶│   Lambda    │───▶│  DynamoDB   │
│             │    │             │    │ Functions   │    │             │
│ • HTML/JS   │    │ • REST API  │    │ • Auth      │    │ • Users     │
│ • Login/Auth│    │ • CORS      │    │ • Products  │    │ • Products  │
│ • Cart UI   │    │ • JWT/local │    │ • Cart      │    │ • Cart      │
│ • Payments  │    │             │    │ • Payments  │    │ • Payments  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Architecture Components

- **Frontend**: HTML/CSS/JavaScript with localStorage-based authentication
- **Backend**: AWS Lambda functions for authentication, products, cart, and payment services
- **Database**: DynamoDB tables for users, products, cart, and payments
- **API**: API Gateway with REST endpoints and user authentication


                ┌──────────────────────────────────────┐
                │        TERRAFORM (IaC Layer)         │
                │--------------------------------------│
                │ - API Gateway                        │
                │ - Lambda Functions                   │
                │ - DynamoDB Tables                    │
                │ - IAM Roles & Permissions            │
                │ - Deployment Automation              │
                └──────────────────────────────────────┘


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

### Authentication
- `POST /auth/register` - Register new user (name, email, password)
- `POST /auth/login` - Login user (email, password)
- Returns user data and stores session in localStorage

### Products
- `GET /products` - List all products

### Cart
- `POST /cart` - Add item to cart (requires authentication)
- `GET /cart?userId={id}` - Get cart items (requires authentication)
- `DELETE /cart?userId={id}&itemId={id}` - Remove item from cart (requires authentication)

### Payment
- `POST /pay` - Process payment (requires authentication)
- `GET /pay` - Get payment history (requires authentication)

## Authentication

The application uses localStorage for client-side session management:
- User data is stored in `localStorage.getItem('currentUser')`
- All protected pages check for authentication on load
- Unauthenticated users are redirected to login page
- Logout clears localStorage and redirects to login

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
