from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            # Test the connection
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
            
            self.db = self.client[settings.DATABASE_NAME]
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise e

    async def close_mongo_connection(self):
        if self.client:
            self.client.close()

    def get_collection(self, collection_name: str):
        if self.db is None:
            raise Exception("Database not connected. Call connect_to_mongo() first.")
        return self.db[collection_name]

mongodb = MongoDB() 