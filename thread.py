from marvin.beta.assistants import Thread as MarvinThread
from marvin.utilities.asyncio import expose_sync_method
from marvin.utilities.openai import get_openai_client


class Thread(MarvinThread):
    @expose_sync_method("load")
    async def load_async(self):
        """
        Loads a thread.
        """
        if self.id is None:
            raise ValueError("Thread cannot be loaded without an id")

        client = get_openai_client()
        response = await client.beta.threads.retrieve(thread_id=self.id)
        self.id = response.id
        self.metadata = response.metadata
        return self
    
    @expose_sync_method("update")
    async def update_async(self, metadata: dict = None):
        """
        Updates a thread.
        """
        if self.id is None:
            raise ValueError("Thread has not been created.")

        client = get_openai_client()

        metadata = metadata if metadata else self.metadata

        response = await client.beta.threads.update(
            thread_id=self.id, metadata=metadata
        )

        self.metadata = response.metadata

        return self