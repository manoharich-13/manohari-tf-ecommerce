import json
import boto3
import pytest
from moto import mock_aws
from manohari_tf_cart_service.cart_lambda import lambda_handler

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

@pytest.fixture
def dynamodb_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

        products = dynamodb.create_table(
            TableName="Products_M",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

        cart = dynamodb.create_table(
            TableName="Cart_M",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "itemId", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "itemId", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        products.wait_until_exists()
        cart.wait_until_exists()

        yield {"products": products, "cart": cart}

def test_add_cart(dynamodb_mock):
    dynamodb_mock["products"].put_item(Item={
        "id": "1",
        "product_name": "Phone",
        "price": 100,
        "availability": 10
    })

    event = {
        "httpMethod": "POST",
        "body": json.dumps({"userId": "u1", "itemId": "1", "quantity": 1})
    }

    res = lambda_handler(event, None)

    assert res["statusCode"] == 200