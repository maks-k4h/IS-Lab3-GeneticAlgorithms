
class Room:
    def __init__(
            self,
            identifier: int,
            capacity: int,
    ) -> None:
        self._identifier = identifier
        self._capacity = capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def identifier(self) -> int:
        return self._identifier
