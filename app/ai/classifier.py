import json

from openai import OpenAI

from app.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL
)

from app.ai.prompts import SYSTEM_PROMPT


class TenderClassifier:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    def classify(self, tender):

        prompt = f"""
Tender Information

Bid Number:
{tender['bid_number']}

Item:
{tender['items']}

Department:
{tender['department']}

Ministry:
{tender['ministry']}

Quantity:
{tender['quantity']}

Analyze this tender semantically.
"""

        response = self.client.chat.completions.create(

            model=OPENAI_MODEL,

            temperature=0,

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        return json.loads(
            response.choices[0].message.content
        )