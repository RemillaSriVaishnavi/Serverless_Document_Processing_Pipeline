import boto3
import json
import statistics
from datetime import datetime

client = boto3.client(
    'stepfunctions',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1'
)

STATE_MACHINE_ARN = "arn:aws:states:us-east-1:000000000000:stateMachine:ClaimProcessor"


def get_execution_times():
    executions = client.list_executions(
        stateMachineArn=STATE_MACHINE_ARN,
        statusFilter='SUCCEEDED'
    )['executions']

    state_times = {
        "VirusScan": [],
        "OCRExtract": [],
        "FinalStore": []
    }

    for exe in executions:
        history = client.get_execution_history(
            executionArn=exe['executionArn']
        )['events']

        state_start = {}
        state_end = {}

        for event in history:
            if 'stateEnteredEventDetails' in event:
                name = event['stateEnteredEventDetails']['name']
                state_start[name] = event['timestamp']

            if 'stateExitedEventDetails' in event:
                name = event['stateExitedEventDetails']['name']
                state_end[name] = event['timestamp']

        for state in state_times.keys():
            if state in state_start and state in state_end:
                duration = (state_end[state] - state_start[state]).total_seconds() * 1000
                state_times[state].append(duration)

    return state_times


def calculate_percentiles(data):
    if not data:
        return {"p50": 0, "p95": 0}

    return {
        "p50": round(statistics.median(data), 2),
        "p95": round(sorted(data)[int(0.95 * len(data)) - 1], 2)
    }


def generate_report():
    state_times = get_execution_times()

    report = {
        "report_summary": {
            "total_executions_analyzed": sum(len(v) for v in state_times.values())
        },
        "state_latency_ms": {}
    }

    for state, times in state_times.items():
        report["state_latency_ms"][state] = calculate_percentiles(times)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    generate_report()