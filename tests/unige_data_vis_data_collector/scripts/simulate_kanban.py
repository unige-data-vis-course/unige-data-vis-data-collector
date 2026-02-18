from datetime import datetime, timedelta

from unige_data_vis_data_collector.kanban_simulator import TicketStatus
from unige_data_vis_data_collector.kanban_simulator.board_engine import IncrementConfig, BoardEngine
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection

if __name__ == "__main__":
    _config = IncrementConfig(
        backlog_entry_period=0.5,
        deployment_period=7,
        status_period={
            TicketStatus.BACKLOG: 2,
            TicketStatus.IN_SCOPING: 2,
            TicketStatus.DONE_SCOPING: 0.5,
            TicketStatus.IN_DEVELOPMENT: 10,
            TicketStatus.DONE_DEVELOPMENT: 2,
            TicketStatus.IN_TESTING: 2
        },
        status_wip_limit={
            TicketStatus.IN_DEVELOPMENT: 3
        }
    )

    start_date = datetime(2026, 1, 1)
    engine = BoardEngine(_config, start_date=start_date)

    tickets = TicketCollection()
    engine.insert_new_tickets(tickets, 10)
    engine.simulate_ticket_list_evolution(tickets)

    print(tickets.board(start_date + timedelta(days=10)))
