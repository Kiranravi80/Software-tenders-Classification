class TenderIndexes:

    @staticmethod
    async def create(collection):

        await collection.create_index(

            "bid_id",

            unique=True

        )

        await collection.create_index(

            "bid_number",

            unique=True

        )

        await collection.create_index(

            "ra_number"

        )

        await collection.create_index(

            "category"

        )

        await collection.create_index(

            "department"

        )

        await collection.create_index(

            "start_date"

        )

        await collection.create_index(

            "end_date"

        )

        print("Indexes Created")