from motor.motor_asyncio import AsyncIOMotorClient
from app.database.indexes import TenderIndexes
from app.config import MONGODB_URL


class MongoDB:

    def __init__(self):

        self.client = None
        self.db = None

    async def connect(self):

        self.client = AsyncIOMotorClient(
            MONGODB_URL
        )

        self.db = self.client["gem_ai"]
        await TenderIndexes.create(

            self.db["tenders"]

        )
        print("✅ Connected to MongoDB")

    async def disconnect(self):

        if self.client:

            self.client.close()

            print("❌ MongoDB Connection Closed")

    def collection(self, name: str):

        return self.db[name]


mongodb = MongoDB()