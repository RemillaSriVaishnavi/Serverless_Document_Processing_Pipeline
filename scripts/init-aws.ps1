# Set awslocal path (IMPORTANT)
$AWSLOCAL="C:\Users\HP\AppData\Roaming\Python\Python311\Scripts\awslocal.exe"

# Create DynamoDB table
& $AWSLOCAL dynamodb create-table `
    --table-name claims `
    --attribute-definitions AttributeName=documentId,AttributeType=S `
    --key-schema AttributeName=documentId,KeyType=HASH `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:4566

# Create SNS topic
& $AWSLOCAL sns create-topic `
    --name claims-dead-letter-topic `
    --endpoint-url http://localhost:4566

# Package Lambdas (paths FIXED)
Compress-Archive -Path ..\src\lambdas\virusScan\* -DestinationPath ..\virusScan.zip -Force
Compress-Archive -Path ..\src\lambdas\ocrExtract\* -DestinationPath ..\ocrExtract.zip -Force
Compress-Archive -Path ..\src\lambdas\finalStore\* -DestinationPath ..\finalStore.zip -Force

# Move back to root
cd ..

# Create Lambda functions

& $AWSLOCAL lambda create-function `
    --function-name virusScan `
    --runtime python3.11 `
    --handler handler.handler `
    --zip-file fileb://virusScan.zip `
    --role arn:aws:iam::000000000000:role/lambda-role `
    --endpoint-url http://localhost:4566

& $AWSLOCAL lambda create-function `
    --function-name ocrExtract `
    --runtime python3.11 `
    --handler handler.handler `
    --zip-file fileb://ocrExtract.zip `
    --role arn:aws:iam::000000000000:role/lambda-role `
    --endpoint-url http://localhost:4566

& $AWSLOCAL lambda create-function `
    --function-name finalStore `
    --runtime python3.11 `
    --handler handler.handler `
    --zip-file fileb://finalStore.zip `
    --role arn:aws:iam::000000000000:role/lambda-role `
    --endpoint-url http://localhost:4566


# Create Step Function

& $AWSLOCAL stepfunctions create-state-machine `
    --name ClaimProcessor `
    --definition file://statemachine/claim-processor.asl.json `
    --role-arn arn:aws:iam::000000000000:role/DummyRole `
    --endpoint-url http://localhost:4566