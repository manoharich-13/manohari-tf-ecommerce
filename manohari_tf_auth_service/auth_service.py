import json
import boto3
import hashlib
import uuid
from boto3.dynamodb.conditions import Key

# --------------------------- 
# Password Hashing
# ---------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# --------------------------- 
# Response Helper
# ---------------------------
def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body)
    }

# --------------------------- 
# MAIN HANDLER
# ---------------------------
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    users_table = dynamodb.Table('users-table')

    print("EVENT:", json.dumps(event))

    method = event.get("httpMethod")
    path = event.get("path", "")

    try:
        if method == "OPTIONS":
            return response(200, {"message": "CORS OK"})

        elif method == "POST" and path.endswith("/register"):
            return register_user(event, users_table)

        elif method == "POST" and path.endswith("/login"):
            return login_user(event, users_table)

        else:
            return response(400, {"message": "Unsupported method or path"})

    except Exception as e:
        print("MAIN ERROR:", str(e))
        return response(500, {"error": str(e)})

# --------------------------- 
# REGISTER USER
# ---------------------------
def register_user(event, users_table):
    try:
        body = json.loads(event.get("body", "{}"))

        name = body.get("name")
        email = body.get("email")
        password = body.get("password")

        if not all([name, email, password]):
            return response(400, {"message": "Name, email, and password are required"})

        # Check if user already exists
        existing = users_table.get_item(Key={"email": email})
        if "Item" in existing:
            return response(409, {"message": "User already exists"})

        # Hash password and create user
        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4())

        users_table.put_item(
            Item={
                "email": email,
                "user_id": user_id,
                "name": name,
                "password": hashed_password
            }
        )

        return response(201, {
            "message": "User registered successfully",
            "user_id": user_id,
            "name": name,
            "email": email
        })

    except Exception as e:
        print("REGISTER ERROR:", str(e))
        return response(500, {"error": str(e)})

# --------------------------- 
# LOGIN USER
# ---------------------------
def login_user(event, users_table):
    try:
        body = json.loads(event.get("body", "{}"))

        email = body.get("email")
        password = body.get("password")

        if not all([email, password]):
            return response(400, {"message": "Email and password are required"})

        # Get user from DynamoDB
        user = users_table.get_item(Key={"email": email})

        if "Item" not in user:
            return response(401, {"message": "Invalid credentials"})

        user_data = user["Item"]

        # Verify password
        if not verify_password(password, user_data["password"]):
            return response(401, {"message": "Invalid credentials"})

        # Return user data (excluding password)
        return response(200, {
            "message": "Login successful",
            "user": {
                "user_id": user_data["user_id"],
                "name": user_data["name"],
                "email": user_data["email"]
            }
        })

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return response(500, {"error": str(e)})