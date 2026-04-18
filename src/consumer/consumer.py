from kafka import KafkaConsumer
import json
import boto3

consumer = KafkaConsumer(
    'claims.incoming',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='claim-processor-group'
)

client = boto3.client(
    'stepfunctions',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1'
)

STATE_MACHINE_ARN = "arn:aws:states:us-east-1:000000000000:stateMachine:ClaimProcessor"

print("Consumer started...")

for msg in consumer:
    data = msg.value
    print(f"Received: {data}")

    response = client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(data)
    )

    print("Started execution:", response["executionArn"])