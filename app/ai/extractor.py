import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.ai.prompts import (
    PDF_EXTRACTION_PROMPT,
    AI_UNDERSTANDING_PROMPT,
)

load_dotenv()


class TenderExtractor:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

from app.ai.prompts import (
    PDF_EXTRACTION_PROMPT,
    AI_UNDERSTANDING_PROMPT
)


class TenderExtractor:

    def __init__(self):

        self.client = OpenAI()

    # ----------------------------------------
    # Phase 3
    # Structured PDF Extraction
    # ----------------------------------------

    def extract(self, pdf_text):

        response = self.client.chat.completions.create(

            model="gpt-4.1",

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": PDF_EXTRACTION_PROMPT
                },
                {
                    "role": "user",
                    "content": pdf_text
                }
            ]

        )

        return json.loads(
            response.choices[0].message.content
        )

    # ----------------------------------------
    # Phase 4
    # AI Tender Understanding
    # ----------------------------------------

    def understand(self, pdf_text):

        response = self.client.chat.completions.create(

            model="gpt-4.1",

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": AI_UNDERSTANDING_PROMPT
                },
                {
                    "role": "user",
                    "content": pdf_text
                }
            ]

        )

        return json.loads(
            response.choices[0].message.content
        )