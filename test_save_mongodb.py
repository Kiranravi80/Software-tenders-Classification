import asyncio

from app.database.mongodb import mongodb


async def main():

    await mongodb.connect()

    print(
        await mongodb.db.command("ping")
    )

    await mongodb.disconnect()


asyncio.run(main())