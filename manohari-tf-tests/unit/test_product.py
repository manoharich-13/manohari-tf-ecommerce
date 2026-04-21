import json
import boto3
import pytest
from moto import mock_aws
from manohari_tf_product_service.product_service import lambda_handler

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

@pytest.fixture
def dynamodb_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

        table = dynamodb.create_table(
            TableName="Products_M",
            KeySchema=[{"AttributeName": "product_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "product_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

        table.wait_until_exists()
        yield table

def test_get_products(dynamodb_mock):
    res = lambda_handler({}, None)

    assert res["statusCode"] == 200