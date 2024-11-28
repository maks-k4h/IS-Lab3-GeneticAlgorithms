from .entities.session import Session


class Schedule:
    def __init__(
            self,
            sessions: list[Session]
    ) -> None:
        self._sessions = sessions

    @property
    def sessions(self) -> list[Session]:
        return self._sessions
