import json
import boto3
import uuid
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

# ---------------------------
# Helper: CORS headers
# ---------------------------
def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }

def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('payments-table')

    # Check API version from header
    api_version = event.get('headers', {}).get('Api-Version', 'v1')
    print(f"API Version: {api_version}")

    method = event.get("httpMethod")

    # ---------------- CORS ----------------
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
            "body": json.dumps({"message": "CORS OK"})
        }

    # ---------------- POST ----------------
    if method == "POST":

        body = json.loads(event.get("body", "{}"))

        payment_id = str(uuid.uuid4())
        user = body.get("user")
        amount = body.get("amount")

        table.put_item(
            Item={
                "payment_id": payment_id,
                "user": user,
                "amount": amount
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Payment successful",
                "payment_id": payment_id,
                "user": user,
                "amount": amount
            })
        }
        


    # ---------------- GET ----------------
    if method == "GET":

        response = table.scan()
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "payments": items
            }, cls=DecimalEncoder)
        }

    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"message": "Unsupported method"})
    }