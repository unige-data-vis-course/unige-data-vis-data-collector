from datetime import datetime
from typing import Optional

from unige_data_vis_data_collector.kanban_simulator import Ticket, TicketStatus


class TicketCollection:
    _tickets: list[Ticket]

    def __init__(self):
        self._tickets = []

    @property
    def tickets(self) -> list[Ticket]:
        return [*self._tickets]

    @property
    def start_date(self) -> Optional[datetime]:
        if len(self) == 0:
            return None
        return min(ticket.start_date for ticket in self._tickets)

    @property
    def end_date(self) -> Optional[datetime]:
        if len(self) == 0:
            return None
        return max(ticket.end_date for ticket in self._tickets)

    def next_ticket_id(self) -> int:
        if len(self) == 0:
            return 1
        return max(t.id for t in self._tickets) + 1

    def count_by_status(self, status: TicketStatus) -> int:
        return len(self.find_by_status(status))

    def find_by_status(self, status: TicketStatus) -> list[Ticket]:
        return [x for x in self._tickets if x.status == status]

    def find_by_status_at(self, status: TicketStatus, at: datetime) -> list[Ticket]:
        return [x for x in self._tickets if x.status_at(at) == status]

    def __len__(self):
        return len(self._tickets)

    def append(self, ticket: Ticket):
        self._tickets.append(ticket)

    def board(self, at: datetime) -> str:
        status_names = [x.name for x in TicketStatus.list()]
        satus_text_max_length = max(len(s) for s in status_names)

        buf = "| " + " | ".join([x.ljust(satus_text_max_length) for x in status_names]) + " |\n"

        status_columns = {x.name: self.find_by_status_at(x, at) for x in TicketStatus.list()}
        max_column_length = max(len(x) for x in status_columns.values())

        rows = []
        for i_row in range(max_column_length):
            rows.append([(status_columns[s][i_row] if i_row < len(status_columns[s]) else None) for s in status_names])
        for row in rows:
            buf += "|"
            for e in row:
                if e is not None:
                    buf += f" {str(e.id).ljust(satus_text_max_length)} |"
                else:
                    buf += (" " * satus_text_max_length) + "  |"
            buf += "\n"
        return buf
