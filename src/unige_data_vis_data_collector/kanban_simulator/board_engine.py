import math
import random
from datetime import datetime, timedelta
from typing import Optional, Callable

from pydantic import BaseModel

from unige_data_vis_data_collector.kanban_simulator import Ticket, TicketStatus
from unige_data_vis_data_collector.kanban_simulator.ticket_collection import TicketCollection


class IncrementConfig(BaseModel):
    # all periods/frequency are in days
    backlog_entry_period: float
    deployment_period: float
    status_period: dict[TicketStatus, float | Callable[[datetime], float]]
    status_wip_limit: dict[TicketStatus, Optional[int] | Callable[[datetime], Optional[int]]]

    def rnd_next_backlog_entry(self, timestamp: datetime) -> datetime:
        return timestamp + timedelta(days=-math.log(random.random()) * self.backlog_entry_period)

    def rnd_status_duration(self, status: TicketStatus, at: datetime) -> timedelta:
        if callable(self.status_period[status]):
            period = self.status_period[status](at)
        else:
            period = self.status_period[status]
        return timedelta(days=-math.log(random.random()) * period)

    def next_deployment_date(self, start_time: datetime, timestamp: datetime) -> datetime:
        """
        deployment is done every deployment_period days, startin on start_time
        :param start_time: the start of time, deployment will be every deployment_period days after this date
        :param timestamp: the current date
        :return: the next deployment date
        """
        nb_days = ((timestamp - start_time).days // self.deployment_period + 1) * (self.deployment_period)
        return start_time + timedelta(days=nb_days)

    def wip_limit(self, status: TicketStatus) -> Callable[[datetime], Optional[int]]:
        def no_limit(_: datetime) -> Optional[int]:
            return None

        if status not in self.status_wip_limit:
            return no_limit
        if callable(self.status_wip_limit[status]):
            return self.status_wip_limit[status]

        return lambda _: self.status_wip_limit[status]


class BoardEngine:
    increment_config: IncrementConfig
    start_date: datetime

    def __init__(self, increment_config: IncrementConfig, start_date: datetime):
        self.increment_config = increment_config
        self.start_date = start_date

    def insert_new_tickets(self, ticket_collection: TicketCollection, nb: int = 1):
        """
        Add a number of tickets to the collection, depending on the backlog entry period and simulate their evolution
        :param ticket_collection: the collection that will be modified
        :param nb: the number of ticket to add (default =1)
        :return: None
        """
        timestamp = ticket_collection.end_date or self.start_date
        for _ in range(nb):
            timestamp = self.increment_config.rnd_next_backlog_entry(timestamp)

            ticket = Ticket(
                ticket_collection.next_ticket_id(),
                TicketStatus.BACKLOG,
                timestamp)
            ticket_collection.append(ticket)

    def simulate_ticket_list_evolution(self, ticket_collection: TicketCollection):
        def status_contraints(status: TicketStatus, at: datetime) -> datetime:
            if self.increment_config.wip_limit(status)(at) is None:
                return at
            return ticket_collection.next_slot_with_status_wip_limit(status, at, self.increment_config.wip_limit(status))

        for ticket in ticket_collection.tickets:
            self.simulate_ticket_evolution(ticket, status_contraints)

    def simulate_ticket_evolution(self, ticket: Ticket, status_constraints: Callable[[TicketStatus, datetime], datetime] = None):
        """
        Ticket is created with a BACKLOG status. We want to populate it with the other statuses, depending on transition frequencies
        The ticket object is updated accordingly
        :param ticket: the ticket to modify
        :param status_constraints: a function that takes a TicketStatus and requested datetime for transition to.
        If defined, it will return the requested timestamp or a later one when some constraints are fullfilled
        :return: None
        """

        # deployment status is based on fixed period
        status_auto = TicketStatus.list()[:-2]
        for st in status_auto:
            td = self.increment_config.rnd_status_duration(st, ticket.end_date)
            requested_date = ticket.end_date + td
            if status_constraints is None:
                actual_date = requested_date
            else:
                actual_date = status_constraints(st.next(), requested_date)
            ticket.update_status(st.next(), actual_date)
        ticket.update_status(TicketStatus.DEPLOYED, self.increment_config.next_deployment_date(self.start_date, ticket.end_date))
