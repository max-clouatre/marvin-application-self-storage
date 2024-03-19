from typing import Dict
from pydantic import BaseModel
from utils import ApplicationStateSerializationUtils


class ApplicationStateBaseModel(BaseModel):
    def serialize_model(self) -> Dict[str, str]:
        return ApplicationStateSerializationUtils.serialize_model(self)

    @classmethod
    def deserialize_model(cls, data: Dict[str, str]) -> "ApplicationStateBaseModel":
        print(cls)
        print(data)
        return ApplicationStateSerializationUtils.deserialize_model(
            model=cls, data=data
        )