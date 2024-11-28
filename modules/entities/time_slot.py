import enum


class TimeSlotDay(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4


class TimeSlotTime(enum.Enum):
    FIRST = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3
    FIFTH = 4
    SIXTH = 5


class TimeSlot:
    def __init__(
            self,
            day: TimeSlotDay,
            time: TimeSlotTime,
    ) -> None:
        self._day = day
        self._time = time

    @property
    def day(self) -> TimeSlotDay:
        return self._day

    @property
    def time(self) -> TimeSlotTime:
        return self._time
