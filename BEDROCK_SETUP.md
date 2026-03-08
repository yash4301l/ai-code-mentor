# Bedrock Setup (Hackathon Fast Path)

This guide connects your backend to Amazon Bedrock Claude with minimal changes.

## 1) AWS prerequisites

- Region: use a Bedrock-supported region (for example `us-east-1` or `ap-south-1` if model access is enabled there).
- In Bedrock console:
  - Open **Model access**.
  - Request/enable access for a Claude model (example: `anthropic.claude-3-haiku-20240307-v1:0`).

## 2) IAM permissions for backend runtime

Attach a policy with at least:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream` (optional)

Scope resource to the model ARN if possible.

## 3) Backend environment variables

Set these where backend runs (EC2/App Runner/etc):

- `AWS_REGION=us-east-1`
- `BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0`
- `BEDROCK_ENABLED=true`

## 4) Python dependency

Install boto3 in backend environment:

```bash
pip install boto3
```

And add to `backend/requirements.txt`:

```txt
boto3>=1.34.0
```

## 5) Minimal code integration pattern

In backend, create a helper that returns structured JSON from Claude.

```python
import json
import os
import boto3

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def classify_and_explain_with_bedrock(code: str, trace: dict, audit: dict) -> dict:
    prompt = f"""
You are a code safety evaluator.
Return STRICT JSON with keys:
- bug_type
- explanation
- claims (array of concise factual claims)
- risk_summary

Code:\n{code}

Trace:\n{json.dumps(trace)}

Audit:\n{json.dumps(audit)}
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 700,
        "temperature": 0,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    payload = json.loads(response["body"].read())
    text = payload["content"][0]["text"]
    return json.loads(text)
```

## 6) Safe fallback

If Bedrock call fails, fallback to your current local simulated explanation so demo never breaks.

## 7) Demo proof points

During demo, explicitly show:

1. Input buggy code
2. Trace + audit catches issue
3. Bedrock explanation is parsed into claims
4. Safety gate blocks unsafe explanation

That directly matches the hackathon AI + AWS evaluation criteria.
