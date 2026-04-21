
import json
import boto3
import pytest
from moto import mock_aws
from manohari_tf_payment_service.payment import lambda_handler

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

@pytest.fixture
def dynamodb_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

        table = dynamodb.create_table(
            TableName="payments-table",
            KeySchema=[{"AttributeName": "payment_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "payment_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

        table.wait_until_exists()
        yield table

def test_payment_post(dynamodb_mock):
    event = {
        "httpMethod": "POST",
        "body": json.dumps({"user": "test", "amount": 100})
    }

    res = lambda_handler(event, None)

    assert res["statusCode"] == 200