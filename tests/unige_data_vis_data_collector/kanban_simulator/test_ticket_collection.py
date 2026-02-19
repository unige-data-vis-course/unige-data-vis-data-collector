from datetime import datetime, timedelta
from unittest import TestCase

from unige_data_vis_data_collector.kanban_simulator import Ticket, TicketStatus
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

_start_date = datetime(2003, 4, 5)


def _dt(nb_days):
    return _start_date + timedelta(nb_days)


def _t(**kwargs) -> Ticket:
    return Ticket(**{"id": 1, "status": TicketStatus.BACKLOG, "timestamp": _start_date, **kwargs})


def _t_with_transitions(id: int, delta_days: list[int]):
    """
    Just pass the number of days between each sequential transitions
    :param id:
    :param delta_days: a list with the same snumber of values as we have TIcket Status
    :return:
    """
    ticket = Ticket(id=id, status=TicketStatus.BACKLOG, timestamp=_dt(delta_days[0]))
    for s, d, in list(zip(TicketStatus.list(), delta_days))[1:]:
        ticket.update_status(s, _dt(d))
    return ticket


class TicketCollectionTest(TestCase):
    def setUp(self):
        self.default_colection = TicketCollection()
        self.default_colection.append(_t(id=1, timestamp=_dt(0)))
        self.default_colection.append(_t(id=2, timestamp=_dt(1)))
        self.default_colection.append(_t(id=3, timestamp=_dt(3)))

    def test_len(self):
        self.assertEqual(3, len(self.default_colection))

    def test_count_by_status(self):
        given = TicketCollection()
        given.append(_t(id=1, status=TicketStatus.DEPLOYED))
        given.append(_t(id=2, status=TicketStatus.IN_DEVELOPMENT))
        given.append(_t(id=3, status=TicketStatus.DEPLOYED))
        given.append(_t(id=4, status=TicketStatus.IN_DEVELOPMENT))
        given.append(_t(id=5, status=TicketStatus.IN_DEVELOPMENT))

        self.assertEqual(0, given.count_by_status(TicketStatus.BACKLOG))
        self.assertEqual(3, given.count_by_status(TicketStatus.IN_DEVELOPMENT))

    def test_start_date(self):
        self.assertEqual(datetime(2003, 4, 5), self.default_colection.start_date)

    def test_end_date(self):
        self.assertEqual(datetime(2003, 4, 8), self.default_colection.end_date)

    def test_next_ticket_id_empty(self):
        given = TicketCollection()
        self.assertEqual(1, given.next_ticket_id())

    def test_next_ticket_id(self):
        self.assertEqual(4, self.default_colection.next_ticket_id())

    def test_next_slot_with_status_wip_limit_empty(self):
        ticket_collection = TicketCollection()

        got = ticket_collection.next_slot_with_status_wip_limit(TicketStatus.IN_TESTING, _start_date, lambda _: 10)
        self.assertEqual(_start_date, got)

    def test_next_slot_with_status_wip_limit_below_wip(self):
        ticket_collection = TicketCollection()
        ticket_collection.append(_t_with_transitions(1, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(2, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 7, 12, 15, 20, 25]))

        got = ticket_collection.next_slot_with_status_wip_limit(TicketStatus.IN_DEVELOPMENT, _dt(8), lambda _: 4)
        self.assertEqual(_dt(8), got)

    def test_next_slot_with_status_wip_limit_above_wip(self):
        ticket_collection = TicketCollection()
        ticket_collection.append(_t_with_transitions(1, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(2, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 7, 12, 15, 20, 25]))

        got = ticket_collection.next_slot_with_status_wip_limit(TicketStatus.IN_DEVELOPMENT, _dt(8), lambda _: 3)
        self.assertEqual(_dt(12) + timedelta(seconds=1), got)

    def test_next_slot_with_status_wip_limit_above_wip_next_slot_not_available(self):
        ticket_collection = TicketCollection()
        ticket_collection.append(_t_with_transitions(1, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(2, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 7, 12, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 11, 14, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 11, 14, 15, 20, 25]))
        ticket_collection.append(_t_with_transitions(3, [0, 4, 5, 11, 17, 18, 20, 25]))

        got = ticket_collection.next_slot_with_status_wip_limit(TicketStatus.IN_DEVELOPMENT, _dt(8), lambda _: 3)
        self.assertEqual(_dt(14) + timedelta(seconds=1), got)
