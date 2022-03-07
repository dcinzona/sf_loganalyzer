from typing import Any


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


class dynamicObj(object):
    """Core class for creating operations.

    Args:
        dict (_type_): _description_
    """

    def __init__(self, *args, **kwargs):
        super(dynamicObj, self).__init__(*args, **kwargs)

    def __getattr__(self, __name: str) -> Any:
        setattr(self, __name, dynamicObj())

    @classmethod
    def from_dict(cls, d: dict):
        for k, v in d.items():
            if isinstance(v, dict):
                setattr(cls, k, dynamicObj.from_dict(v))
            else:
                setattr(cls, k, v)
