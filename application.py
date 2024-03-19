from typing import Type
from marvin.beta import Application as MarvinApplication
from thread import Thread 
from basemodel import ApplicationStateBaseModel

class Application(MarvinApplication):
    state_class: Type[ApplicationStateBaseModel]

    def pre_run_hook(self, run):
        """Load thread metadata into state model before running the assistant."""
        print("pre-run hook: Assistant has started running.")

        thread: Thread = Thread(
            id=run.thread.id,
        ).load()
        print("pre-run hook: loaded thread:", thread)

        thread_metadata = thread.metadata

        if not issubclass(self.state_class, ApplicationStateBaseModel):
            raise ValueError(
                "state_class must be a subclass of ApplicationStateBaseModel"
            )

        if self.state_class and thread_metadata is not None:
            self.state.value = self.state_class.deserialize_model(
                thread_metadata
            )

        else:
            print(
                "pre-run hook: No state model provided or state metadata is empty. Creating new state instance."
            )
            self.state.value = self.state_class()

        print("pre-run hook: STATE ", self.state)

    def post_run_hook(self, run, tool_calls, tool_outputs):
        """ Save state model to thread metadata after running the assistant."""
        print("post_run_hook: Assistant has finished running.")
        print(f"post_run_hook: State: {self.state}")
        self.state.flush_changes()

        thread: Thread = Thread(
            id=run.thread.id,
        )
        thread.metadata = self.state.value.serialize_model()
        thread.update()
        print("post_run_hook: updated thread", thread)