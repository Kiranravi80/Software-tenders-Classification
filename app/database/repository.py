from datetime import datetime
from typing import List, Optional

from app.database.mongodb import mongodb


class TenderRepository:

    def __init__(self):

        self.collection = None

    async def initialize(self):

        self.collection = mongodb.collection(
            "tenders"
        )

    # ----------------------------------------
    # Insert One Tender
    # ----------------------------------------

    async def insert_tender(
        self,
        tender: dict
    ):

        tender["created_at"] = datetime.utcnow()
        tender["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(
            tender
        )

        return result.inserted_id

    # ----------------------------------------
    # Insert Multiple
    # ----------------------------------------

    async def bulk_insert(
        self,
        tenders: List[dict]
    ):

        if not tenders:
            return

        now = datetime.utcnow()

        for tender in tenders:

            tender["created_at"] = now
            tender["updated_at"] = now

        result = await self.collection.insert_many(
            tenders
        )

        return result.inserted_ids

    # ----------------------------------------
    # Find by Bid Number
    # ----------------------------------------

    async def find_by_bid_number(
        self,
        bid_number: str
    ):

        return await self.collection.find_one({

            "bid_number": bid_number

        })

    # ----------------------------------------
    # Find by Bid ID
    # ----------------------------------------

    async def find_by_bid_id(
        self,
        bid_id: int
    ):

        return await self.collection.find_one({

            "bid_id": bid_id

        })

    # ----------------------------------------
    # Update
    # ----------------------------------------

    async def update_tender(
        self,
        bid_id: int,
        data: dict
    ):

        data["updated_at"] = datetime.utcnow()

        return await self.collection.update_one(

            {

                "bid_id": bid_id

            },

            {

                "$set": data

            }

        )
    # ----------------------------------------
    # Save or Update Tender
    # ----------------------------------------

    async def save_tender(
        self,
        tender: dict
    ):

        tender["updated_at"] = datetime.utcnow()

        bid_id = tender["bid_id"]

        existing = await self.collection.find_one(

            {

                "bid_id": bid_id

            },

            {

                "_id": 1

            }

        )

        if existing:

            await self.collection.update_one(

                {

                    "bid_id": bid_id

                },

                {

                    "$set": tender

                }

            )

            return "updated"

        tender["created_at"] = datetime.utcnow()

        await self.collection.insert_one(
            tender
        )

        return "inserted"

    # ----------------------------------------
    # Bulk Save
    # ----------------------------------------

    async def save_many(
        self,
        tenders: list
    ):

        inserted = 0
        updated = 0

        for tender in tenders:

            result = await self.save_tender(
                tender
            )

            if result == "inserted":

                inserted += 1

            else:

                updated += 1

        print()

        print("=" * 50)

        print(f"Inserted : {inserted}")

        print(f"Updated  : {updated}")

        print("=" * 50)

        return {

            "inserted": inserted,

            "updated": updated

        }

    # ----------------------------------------
    # Delete
    # ----------------------------------------

    async def delete_tender(
        self,
        bid_id: int
    ):

        return await self.collection.delete_one({

            "bid_id": bid_id

        })

    # ----------------------------------------
    # Get All
    # ----------------------------------------

    async def get_all(
        self,
        limit=100
    ):

        cursor = self.collection.find()

        return await cursor.to_list(limit)

    # ----------------------------------------
    # Count
    # ----------------------------------------

    async def count(self):

        return await self.collection.count_documents({})

    # ----------------------------------------
    # Exists
    # ----------------------------------------

    async def exists(
        self,
        bid_id: int
    ):

        doc = await self.collection.find_one(

            {

                "bid_id": bid_id

            },

            {

                "_id": 1

            }

        )

        return doc is not None
    # ----------------------------------------
    # Save Embedding
    # ----------------------------------------

    async def save_embedding(

        self,

        bid_id: int,

        embedding: list

    ):

        return await self.collection.update_one(

            {

                "bid_id": bid_id

            },

            {

                "$set": {

                    "embedding": embedding,

                    "updated_at": datetime.utcnow()

                }

            }

        )

repository = TenderRepository()