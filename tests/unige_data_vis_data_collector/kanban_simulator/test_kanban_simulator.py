from datetime import datetime
from unittest import TestCase

from unige_data_vis_data_collector.kanban_simulator import TicketStatus, NoNextStatusException, Ticket


def _ticket_with_history():
    ticket = Ticket(1, TicketStatus.BACKLOG, datetime(2022, 12, 10))
    ticket.update_status(TicketStatus.IN_SCOPING, datetime(2023, 1, 1))
    ticket.update_status(TicketStatus.DONE_SCOPING, datetime(2023, 1, 15))
    ticket.update_status(TicketStatus.IN_DEVELOPMENT, datetime(2023, 2, 1))
    ticket.update_status(TicketStatus.IN_TESTING, datetime(2023, 3, 1))
    ticket.update_status(TicketStatus.DONE_TESTING, datetime(2023, 3, 15))
    ticket.update_status(TicketStatus.DEPLOYED, datetime(2023, 4, 1))
    return ticket


class KanbanSimulatorTest(TestCase):
    def test_status_next(self):
        got = TicketStatus.BACKLOG.next()
        self.assertEqual(TicketStatus.IN_SCOPING, got)

    def test_status_next_last_raises_exception(self):
        with self.assertRaises(NoNextStatusException):
            TicketStatus.DEPLOYED.next()

    def test_ticket_status_at_before(self):
        got = _ticket_with_history().status_at(datetime(2022, 1, 1))
        self.assertIsNone(got)

    def test_ticket_status_at_after(self):
        got = _ticket_with_history().status_at(datetime(2024, 1, 1))
        self.assertEqual(TicketStatus.DEPLOYED, got)

    def test_ticket_status_backlog_day_0(self):
        got = _ticket_with_history().status_at(datetime(2022, 12, 10))
        self.assertEqual(TicketStatus.BACKLOG, got)

    def test_ticket_status_backlog_day_1(self):
        got = _ticket_with_history().status_at(datetime(2022, 12, 11))
        self.assertEqual(TicketStatus.BACKLOG, got)

    def test_ticket_status_in_development(self):
        got = _ticket_with_history().status_at(datetime(2023, 2, 2))
        self.assertEqual(TicketStatus.IN_DEVELOPMENT, got)

    def test_ticket_status_at_bug(self):
        ts = datetime(2026, 1, 11)
        ticket = Ticket(1, TicketStatus.BACKLOG, datetime(2026, 1, 1, 1, 46, 21))
        ticket.update_status(TicketStatus.IN_SCOPING, datetime(2026, 1, 1, 3, 32, 53))
        ticket.update_status(TicketStatus.DONE_SCOPING, datetime(2026, 1, 3, 13, 55, 59))
        ticket.update_status(TicketStatus.IN_DEVELOPMENT, datetime(2026, 1, 4, 3, 42, 3))
        ticket.update_status(TicketStatus.DONE_DEVELOPMENT, datetime(2026, 1, 7, 2, 8, 15))
        ticket.update_status(TicketStatus.IN_TESTING, datetime(2026, 1, 7, 14, 17, 52))
        ticket.update_status(TicketStatus.DONE_TESTING, datetime(2026, 1, 9, 5, 29, 11))
        ticket.update_status(TicketStatus.DEPLOYED, datetime(2026, 1, 15))

        self.assertEqual(TicketStatus.DONE_TESTING, ticket.status_at(ts))
