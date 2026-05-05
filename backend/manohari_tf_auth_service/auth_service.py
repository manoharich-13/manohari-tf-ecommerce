import json
import boto3
import hashlib
import uuid

# --------------------------- 
# DynamoDB Setup
# ---------------------------
def get_table():
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    return dynamodb.Table('users-table')

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
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }

# --------------------------- 
# MAIN LAMBDA HANDLER
# ---------------------------
def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    method = event.get("httpMethod")
    path = event.get("path", "")

    try:
        if method == "OPTIONS":
            
            return {
                "statusCode": 200,
                "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
                "body": ""
            }

        elif method == "POST" and "/auth/login" in path:
            return login_user(event)

        elif method == "POST" and "/auth/register" in path:
            return register_user(event)

        else:
            return response(400, {"message": "Unsupported route"})

    except Exception as e:
        print("MAIN ERROR:", str(e))
        return response(500, {"error": str(e)})

# --------------------------- 
# REGISTER USER
# ---------------------------
def parse_body(event):
    body = event.get("body")

    if body is None:
        return {}

    # If body is already dict (sometimes happens)
    if isinstance(body, dict):
        return body

    # Handle string body
    try:
        return json.loads(body)
    except Exception:
        return {}



def register_user(event):
    users_table = get_table() 
    try:
        body = parse_body(event)

        name = body.get("name")
        email = body.get("email")
        password = body.get("password")

        if not all([name, email, password]):
            return response(400, {"message": "All fields required"})

        # Check if user exists
        existing = users_table.get_item(Key={"email": email})
        if "Item" in existing:
            return response(409, {"message": "User already exists"})

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
def login_user(event):
    users_table = get_table() 
    try:
        body = parse_body(event)

        email = body.get("email")
        password = body.get("password")

        if not all([email, password]):
            return response(400, {"message": "Email and password required"})

        user = users_table.get_item(Key={"email": email}) or {}
        if "Item" not in user:
            return response(401, {"message": "Invalid credentials"})

        user_data = user["Item"]

        if not verify_password(password, user_data["password"]):
            return response(401, {"message": "Invalid credentials"})

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