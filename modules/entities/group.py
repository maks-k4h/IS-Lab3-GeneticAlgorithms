from .subject import Subject


class Group:
    def __init__(
            self,
            name: str,
            size: int,
            subject_requirements: list[tuple[int, Subject]],
    ) -> None:
        self._name = name
        self._size = size
        self._required_subjects: list[tuple[int, Subject]] = subject_requirements

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size

    @property
    def required_subjects(self) -> list[tuple[int, Subject]]:
        return self._required_subjects
