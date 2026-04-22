import json
import boto3
import pytest
from moto import mock_aws
from manohari_tf_auth_service.auth_service import lambda_handler

@pytest.fixture
def dynamodb_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

        users = dynamodb.create_table(
            TableName="users-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

        users.wait_until_exists()

        yield {"users": users}

def test_register_user(dynamodb_mock):
    event = {
        "httpMethod": "POST",
        "path": "/auth/register",
        "body": json.dumps({
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        })
    }

    res = lambda_handler(event, None)

    assert res["statusCode"] == 201
    data = json.loads(res["body"])
    assert data["message"] == "User registered successfully"
    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"
    assert "user_id" in data

def test_register_duplicate_user(dynamodb_mock):
    # First registration
    event1 = {
        "httpMethod": "POST",
        "path": "/auth/register",
        "body": json.dumps({
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        })
    }
    lambda_handler(event1, None)

    # Second registration with same email
    event2 = {
        "httpMethod": "POST",
        "path": "/auth/register",
        "body": json.dumps({
            "name": "Jane Doe",
            "email": "john@example.com",
            "password": "password456"
        })
    }

    res = lambda_handler(event2, None)

    assert res["statusCode"] == 409
    data = json.loads(res["body"])
    assert data["message"] == "User already exists"

def test_login_success(dynamodb_mock):
    # Register user first
    register_event = {
        "httpMethod": "POST",
        "path": "/auth/register",
        "body": json.dumps({
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        })
    }
    lambda_handler(register_event, None)

    # Now login
    login_event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": "john@example.com",
            "password": "password123"
        })
    }

    res = lambda_handler(login_event, None)

    assert res["statusCode"] == 200
    data = json.loads(res["body"])
    assert data["message"] == "Login successful"
    assert data["user"]["email"] == "john@example.com"
    assert data["user"]["name"] == "John Doe"

def test_login_invalid_credentials(dynamodb_mock):
    # Register user first
    register_event = {
        "httpMethod": "POST",
        "path": "/auth/register",
        "body": json.dumps({
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        })
    }
    lambda_handler(register_event, None)

    # Try login with wrong password
    login_event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": "john@example.com",
            "password": "wrongpassword"
        })
    }

    res = lambda_handler(login_event, None)

    assert res["statusCode"] == 401
    data = json.loads(res["body"])
    assert data["message"] == "Invalid credentials"

def test_login_nonexistent_user(dynamodb_mock):
    login_event = {
        "httpMethod": "POST",
        "path": "/auth/login",
        "body": json.dumps({
            "email": "nonexistent@example.com",
            "password": "password123"
        })
    }

    res = lambda_handler(login_event, None)

    assert res["statusCode"] == 401
    data = json.loads(res["body"])
    assert data["message"] == "Invalid credentials"