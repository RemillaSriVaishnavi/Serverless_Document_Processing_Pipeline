import boto3
import os
import json

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")
table = dynamodb.Table("claims")

def handler(event, context):
    document_id = event.get("documentId", "unknown")

    try:
        table.put_item(
            Item={
                "documentId": document_id,
                "status": "processed",
                "data": json.dumps(event)
            },
            ConditionExpression="attribute_not_exists(documentId)"
        )
    except Exception as e:
        print("Duplicate or error:", str(e))

    return event