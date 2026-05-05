import json
import pytest
import hashlib
import sys
import os
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3

# Add parent directory to path so we can import manohari_tf_auth_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the lambda function (adjust the import based on your file name)
# Assuming the lambda code is in a file called lambda_function.py
# from lambda_function import lambda_handler, hash_password, verify_password, response

# For testing purposes, I'll include the functions here
# In practice, you'd import them from your lambda_function.py file

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body)
    }


# ===========================
# FIXTURES
# ===========================

@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing"""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
        
        # Create the table
        table = dynamodb.create_table(
            TableName='users-table',
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123"
    }


@pytest.fixture
def registered_user(dynamodb_table, sample_user_data):
    """Pre-registered user in the database"""
    hashed_password = hash_password(sample_user_data["password"])
    dynamodb_table.put_item(
        Item={
            "email": sample_user_data["email"],
            "user_id": "test-user-id-123",
            "name": sample_user_data["name"],
            "password": hashed_password
        }
    )
    return sample_user_data


# ===========================
# TEST: CORS OPTIONS
# ===========================

@patch('manohari_tf_auth_service.auth_service.get_table')
def test_options_request(mock_get_table):
    """Test CORS preflight OPTIONS request"""
    event = {
        "httpMethod": "OPTIONS",
        "path": "/auth/register"
    }
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in result["headers"]
    body = json.loads(result["body"])
    assert body["message"] == "CORS OK"


# ===========================
# TEST: REGISTER USER
# ===========================

@patch('manohari_tf_auth_service.auth_service.get_table')
def test_register_user_success(mock_get_table, dynamodb_table):
    """Test successful user registration"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/auth/register",
        "body": json.dumps({
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password": "MyPassword456"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert body["message"] == "User registered successfully"
    
    # Verify user was added to database
    db_user = dynamodb_table.get_item(Key={"email": "jane@example.com"})
    assert "Item" in db_user
    assert db_user["Item"]["name"] == "Jane Smith"
    assert db_user["Item"]["email"] == "jane@example.com"
    assert "user_id" in db_user["Item"]
    assert "password" in db_user["Item"]


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_register_user_missing_fields(mock_get_table, dynamodb_table):
    """Test registration with missing required fields"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    test_cases = [
        {"email": "test@example.com", "password": "pass"},  # Missing name
        {"name": "Test User", "password": "pass"},  # Missing email
        {"name": "Test User", "email": "test@example.com"},  # Missing password
        {}  # All fields missing
    ]
    
    for test_body in test_cases:
        event = {
            "httpMethod": "POST",
            "path": "/auth/register",
            "body": json.dumps(test_body)
        }
        
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["message"] == "All fields required"


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_register_user_already_exists(mock_get_table, dynamodb_table, registered_user):
    """Test registration with an email that already exists"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/register",
        "body": json.dumps({
            "name": "Different Name",
            "email": registered_user["email"],
            "password": "DifferentPassword"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 409
    body = json.loads(result["body"])
    assert body["message"] == "User already exists"


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_register_user_invalid_json(mock_get_table, dynamodb_table):
    """Test registration with invalid JSON body"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/register",
        "body": "invalid json{{"
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body


# ===========================
# TEST: LOGIN USER
# ===========================

@patch('manohari_tf_auth_service.auth_service.get_table')
def test_login_user_success(mock_get_table, dynamodb_table, registered_user):
    """Test successful user login"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": registered_user["email"],
            "password": registered_user["password"]
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["message"] == "Login successful"
    assert "user" in body
    assert body["user"]["email"] == registered_user["email"]
    assert body["user"]["name"] == registered_user["name"]
    assert body["user"]["user_id"] == "test-user-id-123"
    assert "password" not in body["user"]  # Password should not be returned


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_login_user_missing_fields(mock_get_table, dynamodb_table):
    """Test login with missing required fields"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    test_cases = [
        {"email": "test@example.com"},  # Missing password
        {"password": "password123"},  # Missing email
        {}  # Both fields missing
    ]
    
    for test_body in test_cases:
        event = {
            "httpMethod": "POST",
            "path": "/auth/login",
            "body": json.dumps(test_body)
        }
        
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["message"] == "Email and password required"


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_login_user_not_found(mock_get_table, dynamodb_table):
    """Test login with non-existent user"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": "nonexistent@example.com",
            "password": "SomePassword123"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 401
    body = json.loads(result["body"])
    assert body["message"] == "Invalid credentials"


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_login_user_wrong_password(mock_get_table, dynamodb_table, registered_user):
    """Test login with incorrect password"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": registered_user["email"],
            "password": "WrongPassword123"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 401
    body = json.loads(result["body"])
    assert body["message"] == "Invalid credentials"


@patch('manohari_tf_auth_service.auth_service.get_table')
def test_login_user_invalid_json(mock_get_table, dynamodb_table):
    """Test login with invalid JSON body"""
    mock_get_table.return_value = dynamodb_table
    
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": "invalid json{{"
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body


# ===========================
# TEST: UNSUPPORTED ROUTES
# ===========================

@patch('manohari_tf_auth_service.auth_service.get_table')
def test_unsupported_route(mock_get_table):
    """Test unsupported route returns 400"""
    from manohari_tf_auth_service.auth_service import lambda_handler
    
    event = {
        "httpMethod": "GET",
        "path": "/api/unknown"
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["message"] == "Unsupported route"


@patch('lambda_function.get_table')
def test_unsupported_method(mock_get_table):
    """Test unsupported HTTP method"""
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "DELETE",
        "path": "/api/register"
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["message"] == "Unsupported route"


# ===========================
# TEST: UTILITY FUNCTIONS
# ===========================

def test_hash_password():
    """Test password hashing is consistent"""
    password = "TestPassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert hash1 == hash2
    assert hash1 != password
    assert len(hash1) == 64  # SHA256 hex digest length


def test_verify_password():
    """Test password verification"""
    password = "MySecurePassword"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_response_structure():
    """Test response helper function structure"""
    result = response(200, {"message": "Test"})
    
    assert result["statusCode"] == 200
    assert "headers" in result
    assert "Access-Control-Allow-Origin" in result["headers"]
    assert result["headers"]["Access-Control-Allow-Origin"] == "*"
    assert "body" in result
    
    body = json.loads(result["body"])
    assert body["message"] == "Test"


# ===========================
# TEST: DATABASE EXCEPTIONS
# ===========================

@patch('lambda_function.get_table')
def test_register_database_error(mock_get_table):
    """Test registration handles database errors gracefully"""
    mock_table = MagicMock()
    mock_table.get_item.side_effect = Exception("Database connection error")
    mock_get_table.return_value = mock_table
    
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/register",
        "body": json.dumps({
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body


@patch('lambda_function.get_table')
def test_login_database_error(mock_get_table):
    """Test login handles database errors gracefully"""
    mock_table = MagicMock()
    mock_table.get_item.side_effect = Exception("Database connection error")
    mock_get_table.return_value = mock_table
    
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/login",
        "body": json.dumps({
            "email": "test@example.com",
            "password": "password123"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body


# ===========================
# TEST: EDGE CASES
# ===========================

@patch('lambda_function.get_table')
def test_empty_body(mock_get_table, dynamodb_table):
    """Test handling of empty request body"""
    mock_get_table.return_value = dynamodb_table
    
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/register",
        "body": ""
    }
    
    result = lambda_handler(event, None)
    
    # Should handle gracefully - either 400 or 500 is acceptable
    assert result["statusCode"] in [400, 500]


@patch('lambda_function.get_table')
def test_missing_body(mock_get_table, dynamodb_table):
    """Test handling of missing body field"""
    mock_get_table.return_value = dynamodb_table
    
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/login"
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] in [400, 500]


@patch('lambda_function.get_table')
def test_special_characters_in_data(mock_get_table, dynamodb_table):
    """Test handling of special characters in user data"""
    mock_get_table.return_value = dynamodb_table
    
    from auth_service import lambda_handler
    
    event = {
        "httpMethod": "POST",
        "path": "/api/register",
        "body": json.dumps({
            "name": "Test User <script>alert('xss')</script>",
            "email": "test+special@example.com",
            "password": "P@ssw0rd!#$%"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result["statusCode"] == 201
    
    # Verify data is stored correctly
    db_user = dynamodb_table.get_item(Key={"email": "test+special@example.com"})
    assert "Item" in db_user


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])