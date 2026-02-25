# flake8: noqa: E303
from datetime import datetime, timedelta

from unige_data_vis_data_collector.kanban_simulator import TicketStatus
from unige_data_vis_data_collector.kanban_simulator.board_engine import IncrementConfig, BoardEngine
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

if __name__ == "__main__":
    start_date = datetime(2026, 1, 1)

    nb_tickets = 400
    def in_dev_wip_limit(at: datetime) -> int:
        nb_days = (at - start_date).days
        if nb_days < 180:
            return 3
        return 6


    def in_dev_period(at: datetime) -> timedelta:
        nb_days = (at - start_date).days
        if nb_days < 360:
            return 10
        return 5


    _config = IncrementConfig(
        backlog_entry_period=0.5,
        deployment_period=7,
        status_period={
            TicketStatus.BACKLOG: 1,
            TicketStatus.IN_SCOPING: 2,
            TicketStatus.DONE_SCOPING: 0.1,
            TicketStatus.IN_DEVELOPMENT: in_dev_period,
            TicketStatus.DONE_DEVELOPMENT: 3,
            TicketStatus.IN_TESTING: 5
        },
        status_wip_limit={
            TicketStatus.IN_DEVELOPMENT: in_dev_wip_limit
        }
    )

    engine = BoardEngine(_config, start_date=start_date)

    tickets = TicketCollection()
    engine.insert_new_tickets(tickets, nb_tickets)
    engine.simulate_ticket_list_evolution(tickets)

    print(tickets.board(start_date + timedelta(days=30)))

    filename_daily_by_status = "out/kanban-daily-by-status.csv"
    filename_ticket_status_transitions = "out/kanban-ticket-status-transitions.csv"
    tickets.csv_daily_count_by_status(filename=filename_daily_by_status)
    tickets.csv_ticket_status_transitions(filename=filename_ticket_status_transitions)
