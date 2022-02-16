from pprint import pp
from typing import Any
import re


class dynamicDict(dict):
    def __init__(self, *args, **kwargs):
        super(dynamicDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
    
    # def __init__(self, *args, **kwargs):
    #     if(args is not None):
    #         self.update(args[0])
    #     elif (kwargs is not None):
    #         self.update(kwargs)

    # def __getattr__(self, item):
    #     object.__setattr__(self, item, None)
    #     return None

    # def __setattr__(self,k,v):
    #     object.__setattr__(self,k,v)

    # @property
    # def __dict__(self):
    #     return self._innerDict

    # def update(self, d:dict):
    #     for k, v in d.items():
    #         self.__setattr__(k, v)

    # def copy(self):
    #     return self.__class__(self._innerDict)

    @classmethod
    def from_dict(cls, d:dict):
        return cls(d)

    @classmethod
    def print(cls):
        cp = cls.__dict__.copy()
        if('parent' in cp):
            cp.pop('parent')
        if('tokens' in cp):
            cp.pop('tokens')
        if('lineSplit' in cp):
            cp.pop('lineSplit')
        pp(cp)

    @property
    def nodeId(self):
        if('eventType' not in self.keys() or self.eventType is  None):
            cp = self.__dict__.copy()
            cp.pop('parent')
            cp.pop('lineSplit')
            cp.pop('tokens')
            print(cp.__str__())
            exit()
            #raise Exception('eventType is None')
        if(self.name.startswith('apex://')):
            self.name = self.name.replace('apex://', '')
        return f'{self.eventType}|{re.escape(self.name.split(":")[0])}'
    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     print('called')
    #     pp(self)
    #     pass
