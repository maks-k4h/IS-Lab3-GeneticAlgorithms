from .room import Room
from .group import Group
from .teacher import Teacher
from .subject import Subject
from .time_slot import TimeSlot


class Session:
    def __init__(
            self,
            room: Room,
            group: Group,
            subject: Subject,
            teacher: Teacher,
            time_slot: TimeSlot,
    ) -> None:
        self._room = room
        self._group = group
        self._subject = subject
        self._teacher = teacher
        self._time_slot = time_slot

    @property
    def room(self) -> Room:
        return self._room

    @room.setter
    def room(self, room: Room):
        self._room = room

    @property
    def group(self) -> Group:
        return self._group

    @group.setter
    def group(self, group: Group):
        self._group = group

    @property
    def subject(self) -> Subject:
        return self._subject

    @subject.setter
    def subject(self, subject: Subject):
        self._subject = subject

    @property
    def teacher(self) -> Teacher:
        return self._teacher

    @teacher.setter
    def teacher(self, teacher: Teacher):
        self._teacher = teacher

    @property
    def time_slot(self) -> TimeSlot:
        return self._time_slot

    @time_slot.setter
    def time_slot(self, time_slot: TimeSlot):
        self._time_slot = time_slot
