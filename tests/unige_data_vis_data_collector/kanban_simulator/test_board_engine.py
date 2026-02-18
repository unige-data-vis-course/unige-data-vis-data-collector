from datetime import datetime, timedelta
from unittest import TestCase

from unige_data_vis_data_collector.kanban_simulator import TicketStatus, Ticket
from unige_data_vis_data_collector.kanban_simulator.board_engine import IncrementConfig, BoardEngine
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

_start_date = datetime(2003, 4, 5)

_config = IncrementConfig(
    backlog_entry_period=0.5,
    deployment_period=7,
    status_period={
        TicketStatus.BACKLOG: 0.5,
        TicketStatus.IN_SCOPING: 2,
        TicketStatus.DONE_SCOPING: 1,
        TicketStatus.IN_DEVELOPMENT: 4,
        TicketStatus.DONE_DEVELOPMENT: 2,
        TicketStatus.IN_TESTING: 2
    }
)


def _t(**kwargs) -> Ticket:
    return Ticket(**{"id": 1, "status": TicketStatus.BACKLOG, "timestamp": datetime(2003, 4, 5), **kwargs})


class BoardEngineTest(TestCase):
    def test_rnd_next_backlog_entry(self):
        got = _config.rnd_next_backlog_entry(_start_date)
        self.assertGreater(got, _start_date)

    def test_insert_new_tickets(self):
        engine = BoardEngine(_config, start_date=_start_date)

        coll = TicketCollection()
        engine.insert_new_tickets(coll, 3)
        self.assertEqual(3, len(coll))
        self.assertGreater(coll.start_date, _start_date)

    def test_next_deployment_date(self):
        given_timestamp = _start_date + timedelta(days=23)
        got = _config.next_deployment_date(_start_date, timestamp=given_timestamp)

        expected_timestamp = _start_date + timedelta(28)
        self.assertEqual(expected_timestamp, got)

    def test_simulate_ticket_evolution(self):
        got = _t()
        engine = BoardEngine(_config, start_date=_start_date)

        engine.simulate_ticket_evolution(got)
        self.assertEqual(TicketStatus.DEPLOYED, got.status)
        self.assertEqual(TicketStatus.DEPLOYED.value, len(got.status_history))
