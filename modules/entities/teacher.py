
from .subject import Subject


class Teacher:
    def __init__(
            self,
            fullname: str,
            teachable_subjects: list[Subject]
    ) -> None:
        self._fullname = fullname
        self._teachable_subjects = teachable_subjects

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def teachable_subjects(self) -> list[Subject]:
        return self._teachable_subjects
