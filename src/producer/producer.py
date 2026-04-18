from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_message(doc_id, text):
    message = {
        "documentId": doc_id,
        "text": text
    }
    producer.send('claims.incoming', message)
    print(f"Sent: {message}")

# Test messages
send_message("1", "normal document")
time.sleep(1)
send_message("2", "this contains fraud")
time.sleep(1)
send_message("1", "duplicate test")  # idempotency test