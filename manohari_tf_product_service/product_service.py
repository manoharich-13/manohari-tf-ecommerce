import json
import boto3
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('Products_M')
    
    # Check API version from header
    api_version = event.get('headers', {}).get('Api-Version', 'v1')
    print(f"API Version: {api_version}")
    
    try:
        response = table.scan()
        items = response.get('Items', [])

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',   # 🔥 FIX
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Api-Version'
            },
            'body': json.dumps(items, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',   # 🔥 FIX
                'Access-Control-Allow-Headers': 'Content-Type,Api-Version'
            },
            'body': json.dumps({"error": str(e)})
        }
        