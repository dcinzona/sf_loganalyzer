from typing import Any


class AttributeInitType(type):
    def __call__(self, *args, **kwargs):
        """Create a new instance."""
        # First, create the object in the normal default way.
        print(f"\nAttributeInitType args: {args}")
        print(f"\nAttributeInitType kwargs: {kwargs}")

        # calls class constructor __init__
        obj = type.__call__(self, *args)

        # Additionally, set attributes on the new object.
        for name, value in kwargs.items():
            setattr(obj, name, value)

        # Return the new object.
        return obj


class dynamicDict(dict):
    """Core class for creating operations.

    Args:
        dict (_type_): _description_
    """

    def __init__(self, *args, **kwargs):
        super(dynamicDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d)


class dynamicObj(object, metaclass=AttributeInitType):
    """Core class for creating operations.

    Args:
        dict (_type_): _description_
    """

    def __getattr__(self, __name: str) -> Any:
        setattr(self, __name, dynamicObj())

    @classmethod
    def from_dict(cls, d: dict):
        for k, v in d.items():
            if isinstance(v, dict):
                setattr(cls, k, dynamicObj.from_dict(v).copy())
            else:
                setattr(cls, k, v.copy())
