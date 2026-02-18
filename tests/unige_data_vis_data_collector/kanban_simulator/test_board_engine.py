from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from unige_data_vis_data_collector.kanban_simulator import TicketStatus, Ticket
from unige_data_vis_data_collector.kanban_simulator.board_engine import IncrementConfig, BoardEngine
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

_start_date = datetime(2003, 4, 5)


def _config():
    return IncrementConfig(
        backlog_entry_period=0.5,
        deployment_period=7,
        status_period={
            TicketStatus.BACKLOG: 0.5,
            TicketStatus.IN_SCOPING: 2,
            TicketStatus.DONE_SCOPING: 1,
            TicketStatus.IN_DEVELOPMENT: 4,
            TicketStatus.DONE_DEVELOPMENT: 2,
            TicketStatus.IN_TESTING: 2
        },
        status_wip_limit={}
    )


def _t(**kwargs) -> Ticket:
    return Ticket(**{"id": 1, "status": TicketStatus.BACKLOG, "timestamp": datetime(2003, 4, 5), **kwargs})


class BoardEngineTest(TestCase):
    def test_rnd_next_backlog_entry(self):
        got = _config().rnd_next_backlog_entry(_start_date)
        self.assertGreater(got, _start_date)

    def test_insert_new_tickets(self):
        engine = BoardEngine(_config(), start_date=_start_date)

        coll = TicketCollection()
        engine.insert_new_tickets(coll, 3)
        self.assertEqual(3, len(coll))
        self.assertGreater(coll.start_date, _start_date)

    def test_next_deployment_date(self):
        given_timestamp = _start_date + timedelta(days=23)
        got = _config().next_deployment_date(_start_date, timestamp=given_timestamp)

        expected_timestamp = _start_date + timedelta(28)
        self.assertEqual(expected_timestamp, got)

    def test_simulate_ticket_evolution(self):
        got = _t()
        engine = BoardEngine(_config(), start_date=_start_date)

        engine.simulate_ticket_evolution(got)
        self.assertEqual(TicketStatus.DEPLOYED, got.status)
        self.assertEqual(TicketStatus.DEPLOYED.value, len(got.status_history))

    def test_simulate_ticket_list_evolution_below_wip(self):
        engine = BoardEngine(_config(), start_date=_start_date)
        engine.increment_config.status_wip_limit = {TicketStatus.IN_DEVELOPMENT: 3}
        seq = [4, 1, 2, 2, 3, 5] * 3
        with patch(
                "unige_data_vis_data_collector.kanban_simulator.board_engine.IncrementConfig.rnd_status_duration",
                side_effect=[timedelta(days=d) for d in seq],
        ):
            ticket_collection = TicketCollection()
            ticket_collection.append(_t(id=1, status=TicketStatus.BACKLOG, timestamp=_start_date))
            ticket_collection.append(_t(id=2, status=TicketStatus.BACKLOG, timestamp=_start_date))
            ticket_collection.append(_t(id=3, status=TicketStatus.BACKLOG, timestamp=_start_date))
            engine.simulate_ticket_list_evolution(ticket_collection)
            self.assertEqual(_start_date + timedelta(days=4 + 1 + 2), ticket_collection.tickets[2].status_history[TicketStatus.IN_DEVELOPMENT])

    def test_simulate_ticket_list_evolution_above_wip(self):
        engine = BoardEngine(_config(), start_date=_start_date)
        engine.increment_config.status_wip_limit = {TicketStatus.IN_DEVELOPMENT: 3}
        seq = [4, 1, 2, 2, 3, 5] * 4
        with patch(
                "unige_data_vis_data_collector.kanban_simulator.board_engine.IncrementConfig.rnd_status_duration",
                side_effect=[timedelta(days=d) for d in seq],
        ):
            ticket_collection = TicketCollection()
            ticket_collection.append(_t(id=1, status=TicketStatus.BACKLOG, timestamp=_start_date))
            ticket_collection.append(_t(id=2, status=TicketStatus.BACKLOG, timestamp=_start_date))
            ticket_collection.append(_t(id=3, status=TicketStatus.BACKLOG, timestamp=_start_date))
            ticket_collection.append(_t(id=4, status=TicketStatus.BACKLOG, timestamp=_start_date))
            engine.simulate_ticket_list_evolution(ticket_collection)
            self.assertEqual(_start_date + timedelta(days=4 + 1 + 2), ticket_collection.tickets[2].status_history[TicketStatus.IN_DEVELOPMENT])
            self.assertEqual(_start_date + timedelta(days=4 + 1 + 2 + (2), seconds=1), ticket_collection.tickets[3].status_history[TicketStatus.IN_DEVELOPMENT])
            self.assertEqual(_start_date + timedelta(days=4 + 1 + 2 + 2 + (2), seconds=1),
                             ticket_collection.tickets[3].status_history[TicketStatus.DONE_DEVELOPMENT],
                             "next status extended by 2 seconds")

            dt = ticket_collection.start_date
            while dt < ticket_collection.end_date:
                nb = ticket_collection.count_by_status_at(TicketStatus.IN_DEVELOPMENT, dt)
                self.assertLessEqual(nb, 3, f"more than 3 IN_DEVELOPMENT tickets at {dt}")
                dt += timedelta(days=1)
