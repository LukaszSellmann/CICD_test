import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Demo Lambda API")

LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "demo-echo-lambda")
LAMBDA_USERS_FUNCTION_NAME = os.getenv("LAMBDA_USERS_FUNCTION_NAME", "demo-users-lambda")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


class InvokeRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/invoke")
def invoke_lambda(request: InvokeRequest):
    try:
        client = boto3.client("lambda", region_name=AWS_REGION)
        payload = {"message": request.message}

        response = client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        result = json.loads(response["Payload"].read())
        return {"lambda_response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users")
def get_users():
    try:
        client = boto3.client("lambda", region_name=AWS_REGION)

        response = client.invoke(
            FunctionName=LAMBDA_USERS_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps({}),
        )

        result = json.loads(response["Payload"].read())
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
