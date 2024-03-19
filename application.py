from typing import Type
from marvin.beta import Application as MarvinApplication
from thread import Thread 
from basemodel import ApplicationStateBaseModel

class MLabApplication(MarvinApplication):
    state_class: Type[ApplicationStateBaseModel]

    def pre_run_hook(self, run):
        """Load thread metadata into state model before running the assistant."""
        print("Assistant has started running.")

        thread: Thread = Thread(
            id=run.thread.id,
        ).load()

        if isinstance(thread.metadata, dict) and len(thread.metadata) > 1:
            thread_metadata = thread.metadata
        else:
            thread_metadata = None
        print("thread_metadata", thread_metadata)

        if not issubclass(self.state_class, ApplicationStateBaseModel):
            raise ValueError(
                "default_state_factory must be a subclass of AIApplicationStateBaseModel"
            )

        if self.state_class and thread_metadata is not None:
            self.state.value = self.state_class.deserialize_model(
                thread_metadata
            )

        else:
            print(
                "No state model provided or state metadata is empty. Creating new state instance."
            )
            self.state.value = self.default_state_factory()

        print("STATE AFTER PRE RUN", self.state)

    def post_run_hook(self, run, tool_calls, tool_outputs):
        """ Save state model to thread metadata after running the assistant."""
        print(f"Assistant {self.name} has finished running.")
        print(f"State: {self.state}")
        self.state.flush_changes()

        # update default thread metadata with self.state.value
        thread: Thread = Thread(
            id=run.thread.id,
        )
        thread.metadata = self.state.value.serialize_model()
        thread.update()
        print("DEFAULT THREAD METADATA STATE AFTER RUN", thread.metadata)