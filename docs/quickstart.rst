Quickstart
==========

Simple application for reading position

.. code-block:: py

    import asyncio

    from wizwalker import WizWalker

    async def print_position(client):
        # position requires memory hooks
        await client.activate_hooks()
        print(await client.body.position())

    async def main():
        walker = WizWalker()

        # we want to ensure walker is closed if there is an error
        try:
            # must have at least one instance open
            client = walker.get_new_clients()[0]

            await print_position(client)

        finally:
            # client can only be used once if not closed
            await walker.close()

    asyncio.run(main())

