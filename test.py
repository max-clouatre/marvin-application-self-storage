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
    name="ToDo App", instructions="A todo application. Update the list of todos with simple tasks. Carefully manipulate state.", state_class=State
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