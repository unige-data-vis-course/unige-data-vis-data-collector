import csv
from collections.abc import Callable
from datetime import datetime, timedelta
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

    def count_by_status_at(self, status: TicketStatus, at: datetime) -> int:
        return len(self.find_by_status_at(status, at))

    def find_by_status_at(self, status: TicketStatus, at: datetime) -> list[Ticket]:
        return [x for x in self._tickets if x.status_at(at) == status]

    def next_slot_with_status_wip_limit(self, status: TicketStatus, at: datetime, wip_limit: Callable[[datetime], int]) -> datetime:
        if wip_limit(at) <= 0:
            raise ValueError("wip_limit must be positive")
        tickets = self.find_by_status_at(status, at)
        if len(tickets) < wip_limit(at):
            return at

        next_status = status.next()
        next_at = min(t.status_history[next_status] for t in self.find_by_status_at(status, at)) + timedelta(seconds=1)
        return self.next_slot_with_status_wip_limit(status, next_at, wip_limit)

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

    def csv_daily_count_by_status(self, filename: str) -> None:
        day = self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "status", "nb"])
            writer.writeheader()
            while day <= self.end_date:
                cpt_day = {}
                for ticket in [t for t in self.tickets]:
                    status = ticket.status_at(day)
                    if status is None:
                        continue
                    cpt_day[status.name] = cpt_day.get(status.name, 0) + 1
                for status, nb in cpt_day.items():
                    writer.writerow({"date": day.isoformat(), "status": status, "nb": nb})
                day += timedelta(days=1)

    def csv_ticket_status_transitions(self, filename: str):
        with open(filename, 'w') as f:
            statuses = TicketStatus.list()
            writer = csv.DictWriter(f, fieldnames=["ticket_id", "start_date", "end_date"] + [st.name for st in statuses])
            writer.writeheader()
            for t in self.tickets:
                row = {"ticket_id": t.id, "start_date": t.start_date.isoformat(), "end_date": t.end_date.isoformat()}
                for st in statuses:
                    ts = t.status_transition_date(st)
                    if ts is not None:
                        ts = ts.isoformat()
                    row[st.name] = ts
                writer.writerow(row)
