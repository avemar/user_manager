class DBWorker:
    def __init__(self, database):
        self.database = database
        self.connection = None
        self.transaction = None

    async def __aenter__(self):
        await self.database.ensure_connected()
        connection = self.database.connect()
        self.connection = await connection.start()
        transaction = self.connection.begin()
        self.transaction = await transaction.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

        await self.transaction.close()
        await self.connection.close()

    async def execute(self, query, *params, **multiparams):
        result = await self.connection.execute(query, *params, **multiparams)
        return result.lastrowid

    async def fetchone(self, query, *params, **multiparams):
        result = await self.connection.execute(query, *params, **multiparams)
        return result.fetchone()

    async def fetchall(self, query, *params, **multiparams):
        result = await self.connection.execute(query, *params, **multiparams)
        return result.fetchall()

    async def commit(self):
        await self.transaction.commit()

    async def rollback(self):
        await self.transaction.rollback()
