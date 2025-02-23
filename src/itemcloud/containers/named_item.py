from itemcloud.size import Size

class NamedItem(Size):
    
    def __init__(self, name: str, width: int, height: int) -> None:
        Size.__init__(self, width, height)
        self._name = name if name is not None else ''
    
    @property
    def name(self) -> str:
        return self._name
    
    
