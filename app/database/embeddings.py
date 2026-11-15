import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class EmbeddingGenerator:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = "text-embedding-3-small"

    # ----------------------------------------

    def build_search_text(
        self,
        tender: dict
    ) -> str:

        sections = []

        sections.append(
            tender.get("items", "")
        )

        sections.append(
            tender.get("category", "")
        )

        sections.append(
            tender.get("reason", "")
        )

        ai = tender.get(
            "ai_analysis",
            {}
        )

        if ai:

            sections.append(
                ai.get("summary", "")
            )

            sections.append(
                ai.get("scope_of_work", "")
            )

            sections.extend(
                ai.get(
                    "required_technologies",
                    []
                )
            )

            sections.extend(
                ai.get(
                    "deliverables",
                    []
                )
            )

            sections.extend(
                ai.get(
                    "keywords",
                    []
                )
            )

        return "\n".join(

            str(s)

            for s in sections

            if s

        )

    # ----------------------------------------

    def generate(
        self,
        tender: dict
    ):

        text = self.build_search_text(
            tender
        )

        response = self.client.embeddings.create(

            model=self.model,

            input=text

        )

        return response.data[0].embedding