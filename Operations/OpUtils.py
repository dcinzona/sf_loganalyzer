from pprint import pp
from typing import Any


class dynamicDict(object):
    def __init__(self, *args, **kwargs):
        if(args is not None):
            self.update(args[0])
        elif (kwargs is not None):
            self.update(kwargs)

    def __getattr__(self, item):
        object.__setattr__(self, item, None)
        return None

    def __setattr__(self,k,v):
        object.__setattr__(self,k,v)

    # @property
    # def __dict__(self):
    #     return self._innerDict

    def update(self, d:dict):
        for k, v in d.items():
            self.__setattr__(k, v)

    def copy(self):
        return self.__class__(self._innerDict)

    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     print('called')
    #     pp(self)
    #     pass
