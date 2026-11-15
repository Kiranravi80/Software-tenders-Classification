from app.database.mongodb import mongodb
from app.database.embeddings import EmbeddingGenerator


class VectorStore:

    def __init__(self):

        self.collection = None

        self.embedder = EmbeddingGenerator()

    async def initialize(self):

        self.collection = mongodb.collection(
            "tenders"
        )

    # ----------------------------------------

    async def vector_search(

        self,

        query: str,

        limit: int = 10

    ):

        embedding = self.embedder.generate(
            {
                "items": query
            }
        )

        pipeline = [

            {

                "$vectorSearch": {

                    "index": "tender_vector_index",

                    "path": "embedding",

                    "queryVector": embedding,

                    "numCandidates": 100,

                    "limit": limit

                }

            },

            {

                "$project": {

                    "_id": 0,

                    "bid_id": 1,

                    "bid_number": 1,

                    "items": 1,

                    "category": 1,

                    "department": 1,

                    "ministry": 1,

                    "confidence": 1,

                    "score": {

                        "$meta": "vectorSearchScore"

                    }

                }

            }

        ]

        return await self.collection.aggregate(
            pipeline
        ).to_list(length=limit)


vector_store = VectorStore()