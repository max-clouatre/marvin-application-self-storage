---
title: Marvin Self-Storing Application
description: A MarvinAI Application wrapper for self-storing state
tags:
  - fastapi
  - python
  - marvin
  - openai
---

# MarvinAI Application State Management Wrapper

This repo introduces a few helpful utilities around [MarvinAI Applications](https://www.askmarvin.ai/docs/interactive/applications/) to allow for self-storing state within OpenAI Thread metadata.

## [Marvin Thread](https://www.askmarvin.ai/docs/interactive/assistants/#threads) Additions

- Add load() method to load thread and metadata
- Add update() method to update thread with metadata

```python
from marvin.beta.assistants import Thread as MarvinThread

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
        print(f'Updating thread:{self.id}, {metadata}')
        if self.id is None:
            raise ValueError("Thread has not been created.")

        client = get_openai_client()

        metadata = metadata if metadata else self.metadata

        response = await client.beta.threads.update(
            thread_id=self.id, metadata=metadata
        )

        self.metadata = response.metadata

        return self
```

## Example

### (Available in test.py)

```python
from datetime import datetime
from pydantic import BaseModel
from thread import Thread
from basemodel import ApplicationStateBaseModel
from application import Application
from marvin.beta.assistants import pprint_messages


# step 1: create a thread
thread = Thread().create()

# step 2: Define the application state
class Task(BaseModel):
    description: str
    due: datetime
    done: bool = False

class State(ApplicationStateBaseModel):
    todos: list[Task] = []

# step 3: Define the application
todo_app = Application(
    name="ToDo App",
    instructions="A todo application. Update the list of todos with simple tasks. Carefully manipulate state.",
    state_class=State
)

# step 4: Interact with the application
todo_app.say("I need to go to the store tomorrow afternoon", thread=thread)

# step 5: Load the thread to view the metadata
thread_with_metadata = Thread(id=thread.id).load()
print("--Thread metadata--", thread_with_metadata.metadata)

#  Finish one
todo_app.say("I went to the store", thread=thread)

# ask a question
todo_app.say("Show me my todos")

# print the entire thread
pprint_messages(thread.get_messages())

# load the thread to view the metadata again
thread_with_metadata = Thread(id=thread.id).load()
print("--Thread metadata--", thread_with_metadata.metadata)
```
