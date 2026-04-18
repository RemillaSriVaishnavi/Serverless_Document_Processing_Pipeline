def handler(event, context):
    event["scanStatus"] = "clean"
    return event