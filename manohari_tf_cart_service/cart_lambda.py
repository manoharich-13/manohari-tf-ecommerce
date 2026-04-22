import json
import boto3
from boto3.dynamodb.conditions import Key
import decimal

# ---------------------------
# Decimal Encoder
# ---------------------------
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


# ---------------------------
# Response
# ---------------------------
def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }


# ---------------------------
# MAIN HANDLER
# ---------------------------
def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    products_table = dynamodb.Table('Products_M')
    cart_table = dynamodb.Table('Cart_M')

    # Check API version from header
    api_version = event.get('headers', {}).get('Api-Version', 'v1')
    print(f"API Version: {api_version}")

    print("EVENT:", json.dumps(event))

    method = event.get("httpMethod")

    try:
        if method == "OPTIONS":
            return response(200, {"msg": "ok"})

        elif method == "POST":
            return add_to_cart(event, products_table, cart_table)

        elif method == "GET":
            return get_cart(event, cart_table)

        elif method == "DELETE":
            return delete_from_cart(event, cart_table)

        else:
            return response(400, {"message": "Unsupported method"})

    except Exception as e:
        print("MAIN ERROR:", str(e))
        return response(500, {"error": str(e)})


# ---------------------------
# ADD TO CART
# ---------------------------
def safe_int(value):
    try:
        return int(value)
    except:
        return 0
        
def add_to_cart(event, products_table, cart_table):
    try:
        body = json.loads(event.get("body") or "{}")

        user_id = str(body.get("userId"))
        item_id = str(body.get("itemId"))
        quantity = int(body.get("quantity", 1))

        product = products_table.get_item(Key={"id": item_id})

        if "Item" not in product:
            return response(404, {"message": "Product not found"})

        p = product["Item"]

        # ✅ SAFE CONVERSION
        stock = safe_int(p.get("availability"))
        price = safe_int(p.get("price"))
        name = str(p.get("product_name", ""))

        if stock <= 0:
            return response(400, {"message": "Out of stock"})

        existing = cart_table.get_item(
            Key={"userId": user_id, "itemId": item_id}
        )

        if "Item" in existing:

            new_qty = safe_int(existing["Item"]["quantity"]) + quantity

            cart_table.update_item(
                Key={"userId": user_id, "itemId": item_id},
                UpdateExpression="SET quantity=:q, total_price=:t",
                ExpressionAttributeValues={
                    ":q": new_qty,
                    ":t": new_qty * price
                }
            )

        else:
            cart_table.put_item(
                Item={
                    "userId": user_id,
                    "itemId": item_id,
                    "product_name": name,
                    "price": price,
                    "quantity": quantity,
                    "total_price": price * quantity
                }
            )

        return response(200, {"message": "Added to cart"})

    except Exception as e:
        print("ERROR:", str(e))   # 🔥 IMPORTANT LOG
        return response(500, {"error": str(e)})
# ---------------------------
# GET CART
# ---------------------------
def get_cart(event, cart_table):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")

        if not user_id:
            return response(400, {"message": "userId required"})

        result = cart_table.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )

        return response(200, result.get("Items", []))

    except Exception as e:
        print("GET ERROR:", str(e))
        return response(500, {"error": str(e)})


# ---------------------------
# DELETE
# ---------------------------
def delete_from_cart(event, cart_table):
    try:
        params = event.get("queryStringParameters") or {}

        user_id = params.get("userId")
        item_id = params.get("itemId")

        if not user_id or not item_id:
            return response(400, {"message": "Missing params"})

        cart_table.delete_item(
            Key={"userId": user_id, "itemId": item_id}
        )

        return response(200, {"message": "Deleted"})

    except Exception as e:
        print("DELETE ERROR:", str(e))
        return response(500, {"error": str(e)})