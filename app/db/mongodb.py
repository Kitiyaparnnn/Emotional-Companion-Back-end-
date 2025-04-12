from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]

    async def close_mongo_connection(self):
        self.client.close()

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

mongodb = MongoDB() 