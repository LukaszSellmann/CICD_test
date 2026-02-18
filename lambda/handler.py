import json


def lambda_handler(event, context):
    message = event.get("message", "no message provided")

    return {
        "statusCode": 200,
        "echo": message,
        "source": "demo-echo-lambda",
    }
