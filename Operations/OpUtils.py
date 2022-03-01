from pprint import pp
import base64


class dynamicDict(dict):
    def __init__(self, *args, **kwargs):
        super(dynamicDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def from_dict(cls, d: dict):
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
        if(self.get('_nodeId', None) is None):
            if('eventType' not in self.keys() or self.eventType is None):
                cp = self.__dict__.copy()
                cp.pop('parent')
                cp.pop('lineSplit')
                cp.pop('tokens')
                print(cp.__str__())
                exit()
            name = f'{self.eventType}|{self.name}'
            self._nodeId = base64.b64encode(
                name.encode('utf-8')).decode('utf-8')
        return self._nodeId
