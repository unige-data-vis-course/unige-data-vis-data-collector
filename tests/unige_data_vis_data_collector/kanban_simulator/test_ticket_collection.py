from datetime import datetime
from unittest import TestCase

from unige_data_vis_data_collector.kanban_simulator import Ticket, TicketStatus
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection


def _t(**kwargs) -> Ticket:
    return Ticket(**{"id": 1, "status": TicketStatus.BACKLOG, "timestamp": datetime(2003, 4, 5), **kwargs})


class TicketCollectionTest(TestCase):
    def setUp(self):
        self.default_colection = TicketCollection()
        self.default_colection.append(_t(id=1, timestamp=datetime(2003, 4, 5)))
        self.default_colection.append(_t(id=2, timestamp=datetime(2003, 4, 6)))
        self.default_colection.append(_t(id=3, timestamp=datetime(2003, 4, 8)))

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
