# flake8: noqa: E303
from datetime import datetime, timedelta

from unige_data_vis_data_collector.kanban_simulator import TicketStatus
from unige_data_vis_data_collector.kanban_simulator.board_engine import IncrementConfig, BoardEngine
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

if __name__ == "__main__":
    start_date = datetime(2026, 1, 1)


    def in_dev_wip_limit(at: datetime) -> int:
        nb_days = (at - start_date).days
        print(f"{at} - {start_date}: {nb_days}")
        if nb_days < 90:
            return 3
        return 6


    def in_dev_period(at: datetime) -> timedelta:
        nb_days = (at - start_date).days
        if nb_days < 180:
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
    engine.insert_new_tickets(tickets, 200)
    engine.simulate_ticket_list_evolution(tickets)

    print(tickets.board(start_date + timedelta(days=30)))

    tickets.csv_daily_count_by_status("out/kanban-daily-count-by-status.csv")
