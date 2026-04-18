def handler(event, context):
    text = event.get("text", "")

    # Add fraud keyword if present in input
    if "fraud" in text.lower():
        event["extractedText"] = text + " fraud detected"
    else:
        event["extractedText"] = text + " processed"

    return event