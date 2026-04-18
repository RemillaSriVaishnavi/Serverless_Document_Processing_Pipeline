# Document Processing Pipeline (Event-Driven Architecture)

## Overview

This project implements a **production-grade event-driven document processing pipeline** using:

* **Apache Kafka (Strimzi on Kubernetes)** for event streaming
* **AWS Step Functions (via LocalStack)** for orchestration
* **Lambda functions** for processing
* **DynamoDB** for storage
* **SNS** for failure handling (Dead Letter Queue)

The system simulates how modern **fintech/insurtech platforms** process high-volume asynchronous workflows with reliability, scalability, and fault tolerance.

## Architecture

```
Producer → Kafka (claims.incoming)
          ↓
     Kafka Consumer
          ↓
   Step Functions (Orchestration)
          ↓
 ┌────────┬──────────────┬─────────────┐
 │VirusScan │ OCRExtract │ FraudCheck │
 └────────┴──────────────┴─────────────┘
                    ↓
          HumanReviewQueue (if fraud)
                    ↓
              FinalStore Lambda
                    ↓
        DynamoDB (claims table)
                    ↓
 Kafka (claims.processed topic)
```

## Technologies Used

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Orchestration    | AWS Step Functions (LocalStack) |
| Messaging        | Apache Kafka (Strimzi)          |
| Compute          | AWS Lambda (Python)             |
| Database         | DynamoDB                        |
| Containerization | Docker                          |
| Kubernetes       | Minikube                        |
| IaC              | PowerShell Script               |
| Monitoring       | Python (boto3)                  |


## Project Structure

```
document-processing-pipeline/
│
├── docker-compose.yml
├── .env.example
├── submission.json
├── README.md
│
├── k8s/
│   ├── kafka-cluster.yml
│   └── kafka-topics.yml
│
├── statemachine/
│   └── claim-processor.asl.json
│
├── scripts/
│   └── init-aws.ps1
│
├── src/
│   ├── lambdas/
│   │   ├── virusScan/
│   │   ├── ocrExtract/
│   │   └── finalStore/
│   │
│   ├── producer/
│   │   └── producer.py
│   │
│   ├── consumer/
│   │   └── consumer.py
│   │
│   └── monitoring/
│       └── generate_report.py
```

## Data Flow

1. **Producer**

   * Sends JSON message to Kafka topic `claims.incoming`

2. **Consumer**

   * Reads message from Kafka
   * Triggers Step Function execution

3. **Step Function Workflow**

   * `VirusScan` → validates file
   * `OCRExtract` → extracts text
   * `FraudDetection` → checks for keyword "fraud"
   * `HumanReviewQueue` → wait state (if fraud)
   * `FinalStore` → saves result

4. **Final Output**

   * Stored in DynamoDB (`claims` table)
   * Event published to Kafka (`claims.processed`)

5. **Failure Handling**

   * Errors sent to SNS Dead Letter Topic


## Idempotency

* Implemented in `FinalStore` Lambda using:

```
ConditionExpression: attribute_not_exists(documentId)
```

* Prevents duplicate records
* Ensures safe reprocessing


## Retry & Error Handling

* Retry configured for:

  * `VirusScan`
  * `OCRExtract`

* Global `Catch` block:

  * Sends failures to SNS DLQ


## Setup Instructions

### 1️. Start LocalStack

```bash
docker-compose up -d
```

### 2️. Start Minikube

```bash
minikube start --memory=4096 --cpus=2
```

### 3️. Install Strimzi

```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
```

### 4️. Deploy Kafka

```bash
kubectl apply -f k8s/kafka-cluster.yml
kubectl apply -f k8s/kafka-topics.yml
```

### 5️. Provision AWS Resources

```bash
cd scripts
powershell -ExecutionPolicy Bypass -File init-aws.ps1
```

### 6️. Run Kafka Port Forward

```bash
kubectl port-forward svc/my-cluster-kafka-bootstrap 9092:9092 -n kafka
```

### 7️. Start Consumer

```bash
cd src/consumer
python consumer.py
```

### 8️. Run Producer

```bash
cd src/producer
python producer.py
```


## Monitoring & Reporting

Run:

```bash
cd src/monitoring
python generate_report.py
```

### Output Example:

```json
{
  "report_summary": {
    "total_executions_analyzed": 6
  },
  "state_latency_ms": {
    "VirusScan": { "p50": 5.2, "p95": 8.1 },
    "OCRExtract": { "p50": 6.3, "p95": 9.0 },
    "FinalStore": { "p50": 4.8, "p95": 7.2 }
  }
}
```

## Features

✔ Event-driven architecture
✔ Scalable Kafka messaging
✔ Serverless orchestration
✔ Retry & fault tolerance
✔ Dead-letter queue handling
✔ Idempotent processing
✔ Monitoring with latency metrics


## Security Considerations

* No hardcoded secrets
* Uses local endpoints
* IAM roles mocked in LocalStack

## Conclusion

This project demonstrates how to build a **resilient, scalable, and production-ready event-driven pipeline**, simulating real-world systems used in **financial and enterprise platforms**.
