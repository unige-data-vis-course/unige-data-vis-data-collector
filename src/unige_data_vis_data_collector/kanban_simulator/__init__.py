from datetime import datetime
from enum import Enum
from typing import Optional


class NoNextStatusException(Exception):
    pass


class NoPreviousStatusException(Exception):
    pass


class TicketStatus(Enum):
    """
    SEquence of ticket statuses. Must be incremented by one to navigate previous/next
    """
    BACKLOG = 1
    IN_SCOPING = 2
    DONE_SCOPING = 3
    IN_DEVELOPMENT = 4
    DONE_DEVELOPMENT = 5
    IN_TESTING = 6
    DONE_TESTING = 7
    DEPLOYED = 8

    @staticmethod
    def first_status() -> "TicketStatus":
        return TicketStatus.BACKLOG

    @staticmethod
    def last_status() -> "TicketStatus":
        return TicketStatus.DEPLOYED

    @staticmethod
    def before_last_status() -> "TicketStatus":
        return TicketStatus.DONE_TESTING

    @staticmethod
    def list() -> list["TicketStatus"]:
        return sorted(TicketStatus, key=lambda x: x.value)

    def next(self) -> "TicketStatus":
        """
        return the previous status in the sequential list. Raises for the last one.
        :return:
        """
        if self == self.__class__.DEPLOYED:
            raise NoNextStatusException(f"No next status for {self}")
        return self.__class__(self.value + 1)

    def previous(self) -> "TicketStatus":
        """
        returns the next status in the sequential list. Raises for the first one
        :return:
        """
        if self == self.__class__.BACKLOG:
            raise NoPreviousStatusException(f"No previsous status for {self}")
        return self.__class__(self.value - 1)

    def __str__(self):
        return self.name


class Ticket:
    id: int
    status: TicketStatus
    status_history: dict[TicketStatus, datetime]

    def __init__(self, id: int, status: TicketStatus, timestamp: datetime):
        self.id = id
        self.status_history = {}
        self.update_status(status, timestamp)

    def update_status(self, status: TicketStatus, timestamp: datetime):
        self.status_history[status] = timestamp
        self.status = status

    def status_transition_date(self, status: TicketStatus) -> Optional[datetime]:
        return self.status_history.get(status)

    @property
    def start_date(self) -> datetime:
        return min(self.status_history.values())

    @property
    def end_date(self) -> datetime:
        return max(self.status_history.values())

    def _delta_time_between_status(self, from_status: TicketStatus, to_status: TicketStatus) -> Optional[float]:
        end = self.status_transition_date(from_status)
        start = self.status_transition_date(to_status)
        if end is None or start is None:
            return None
        return (end - start).total_seconds() / (24 * 3600)

    @property
    def lead_time_days(self) -> Optional[float]:
        return self._delta_time_between_status(TicketStatus.DEPLOYED, TicketStatus.BACKLOG)

    @property
    def cycles_time_days(self) -> Optional[float]:
        return self._delta_time_between_status(TicketStatus.DEPLOYED, TicketStatus.DONE_SCOPING)

    def status_at(self, timestamp: datetime) -> Optional[TicketStatus]:
        if timestamp < self.start_date:
            return None
        if timestamp >= self.end_date:
            return TicketStatus.DEPLOYED

        prev_status = TicketStatus.BACKLOG
        for status, ts in sorted(self.status_history.items(), key=lambda x: x[1]):
            if ts > timestamp:
                return prev_status
            prev_status = status
        raise Exception("Out of bound status_at")

    def __str__(self):
        buf = f"Ticket {self.id}: {self.status.name}"
        for status, timestamp in sorted(self.status_history.items(), key=lambda x: x[1]):
            buf += f"\n\t{status.name} at {timestamp}"
        return buf
