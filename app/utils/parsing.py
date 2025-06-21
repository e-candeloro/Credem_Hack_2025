import json


def parse_json_response(text, _):
    try:
        text = text.strip()
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3].strip()
        return json.loads(text)
    except:
        return {k: "Error" for k in ["Nome", "Cognome", "Data", "Cluster"]}
