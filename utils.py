from typing import Dict, Any, Literal, Type, get_args, get_origin
from pydantic import BaseModel
import json
from pydantic.fields import FieldInfo



class TypeUtils:
    """
    Utility class for inspecting types.
    """

    @staticmethod
    def is_list_type(field: FieldInfo) -> bool:
        """
        Determine if the given field type is a list or contains list type annotations.

        Args:
            field (FieldInfo): The field to check.

        Returns:
            bool: True if the field is a list type, False otherwise.
        """
        # Recursively check if field annotation itself is a list type
        if hasattr(field, "annotation") and field.annotation is not None:
            return TypeUtils.is_list_type(field.annotation)

        # Determine if the field's origin is a list or a subclass of list
        origin = get_origin(field)
        if origin is list or (origin is not None and issubclass(origin, list)):
            return True

        # Check if the field has type arguments, indicating it could be a generic list type
        args = get_args(field)
        return bool(args)

    @staticmethod
    def is_list_of_basemodels_type(field: FieldInfo) -> bool:
        """
        Check if the given field type is a list of BaseModel instances.

        Args:
            field (Type): The field to check.

        Returns:
            bool: True if the field is a list of BaseModel instances, False otherwise.
        """
        # First, ensure the field is a list type
        if not TypeUtils.is_list_type(field):
            return False

        if hasattr(field, "annotation") and field.annotation is not None:
            args = get_args(field.annotation)

            if args:
                arg_class = args[0]
                return issubclass(arg_class, BaseModel)
            else:
                return False

        args = get_args(field)
        if not args:
            return False
        return issubclass(args[0], BaseModel)

    @staticmethod
    def is_basemodel_type(field: FieldInfo) -> bool:
        """
        Check if the input type is a BaseModel type.

        Args:
            input_type (FieldInfo): The field to check.

        Returns:
            bool: True if the input type is a BaseModel type, False otherwise.
        """
        try:
            return issubclass(field, BaseModel)
        except TypeError:
            return False

    @staticmethod
    def is_literal_type(field: FieldInfo) -> bool:
        """
        Check if the input type is a Literal type.

        Args:
            input_type (FieldInfo): The field to check.

        Returns:
            bool: True if the input type is a Literal type, False otherwise.
        """
        if hasattr(field, "annotation") and field.annotation is not None:
            return TypeUtils.is_literal_type(field.annotation)

        return get_origin(field) is Literal
    
class ApplicationStateSerializationUtils:
    @staticmethod
    def serialize_value(value: str, field: FieldInfo) -> str:
        """
        Serialize a value to a JSON-compatible string.

        Args:
            value (Any): The value to serialize.

        Returns:
            str: The serialized JSON string.
        """
        if value is None:
            return json.dumps(None)

        if TypeUtils.is_literal_type(field):
            return value

        if isinstance(value, BaseModel):
            return value.model_dump_json()
        elif isinstance(value, list) and all(
            isinstance(item, BaseModel) for item in value
        ):
            return json.dumps([item.model_dump_json() for item in value])
        else:
            return json.dumps(value)

    @staticmethod
    def deserialize_value(value: str, field: FieldInfo) -> Any:
        """
        Deserialize a value from a JSON string according to the specified field type.

        Args:
            value (str): The JSON string to deserialize.
            field (Type): The field type that informs how to deserialize the value.

        Returns:
            Any: The deserialized value.
        """
        if value is None:
            return None

        if value == "null":
            return None

        if value == "[]":
            return []

        if TypeUtils.is_literal_type(field):
            return value

        if TypeUtils.is_list_of_basemodels_type(field):
            if hasattr(field, "annotation") and field.annotation is not None:
                if get_args(field.annotation):
                    arg_class = get_args(field.annotation)[0]
                    return [arg_class(**json.loads(item)) for item in json.loads(value)]

            subclass = get_args(field)[0]
            return [subclass(**json.loads(item)) for item in json.loads(value)]

        if TypeUtils.is_basemodel_type(field):
            return field.model_load_json(value)

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def serialize_model(model: BaseModel) -> Dict[str, str]:
        """
        Serialize a model into a dictionary of field names to serialized values.

        Args:
            model (BaseModel): The model to serialize.

        Returns:
            Dict[str, str]: A dictionary mapping field names to serialized values.
        """
        serialized_data = {}
        for field_name, field in model.model_fields.items():
            value = getattr(model, field_name)
            serialized_data[field_name] = (
                ApplicationStateSerializationUtils.serialize_value(value, field)
            )
        return serialized_data

    @staticmethod
    def deserialize_model(model: BaseModel, data: Dict[str, str]) -> Type[BaseModel]:
        """
        Deserialize a model from a dictionary of field names to serialized values.

        Args:
            data (Dict[str, str]): The dictionary of serialized field values.

        Returns:
            AIApplicationStateBaseModel: An instance of the model populated with deserialized field values.
        """
        deserialized_data = {}
        for field_name, value in data.items():
            field = model.model_fields.get(field_name)
            deserialized_data[field_name] = (
                ApplicationStateSerializationUtils.deserialize_value(value, field)
            )
        return model(**deserialized_data)
