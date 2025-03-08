from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Enumerations
class TicketStatus(Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    REFUNDED = "REFUNDED"

class OrderStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class RefundStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Classes
class User:
    def __init__(self, id: int, name: str, email: str, role: str):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__role = role

    # Getter for id
    @property
    def id(self):
        return self.__id

    # Getter and setter for name
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    # Getter and setter for email
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value: str):
        self.__email = value

    # Getter and setter for role
    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, value: str):
        self.__role = value

class EventOrganizer(User):
    def __init__(self, id: int, name: str, email: str, role: str):
        super().__init__(id, name, email, role)
        self.__events: List['Event'] = []

    # Getter for events
    @property
    def events(self):
        return self.__events

    def create_event(self, event_id: int, name: str, date: datetime, hall: 'Hall') -> 'Event':
        event = Event(id=event_id, name=name, date=date, organizer=self, hall=hall)
        self.__events.append(event)
        logging.info(f"Event '{name}' created by {self.name}.")
        return event

class Buyer(User):
    def __init__(self, id: int, name: str, email: str, role: str):
        super().__init__(id, name, email, role)
        self.__tickets: List['Ticket'] = []
        self.__orders: List['Order'] = []

    # Getter for tickets
    @property
    def tickets(self):
        return self.__tickets

    # Getter for orders
    @property
    def orders(self):
        return self.__orders

    def purchase_tickets(self, event: 'Event', zone_type: str, quantity: int) -> Optional['Order']:
        zone = event.zones.get(zone_type)
        if not zone:
            logging.error(f"Zone '{zone_type}' not found in event '{event.name}'.")
            return None

        available_tickets = zone.get_available_tickets(quantity)
        if len(available_tickets) < quantity:
            logging.error(f"Not enough tickets available in zone '{zone_type}'.")
            return None

        order = Order(id=len(self.__orders) + 1, buyer=self)
        for ticket in available_tickets:
            if not ticket.purchase(self):
                logging.error(f"Failed to purchase ticket {ticket.id}.")
                return None
            order.add_ticket(ticket)

        if order.complete_order():
            logging.info(f"Order {order.id} completed successfully.")
            return order
        else:
            logging.error(f"Failed to complete order {order.id}.")
            return None

    def request_refund(self, ticket_id: int) -> Optional['RefundRequest']:
        ticket = next((t for t in self.__tickets if t.id == ticket_id), None)
        if not ticket:
            logging.error(f"Ticket {ticket_id} not found.")
            return None

        if ticket.status != TicketStatus.SOLD:
            logging.error(f"Ticket {ticket_id} is not eligible for refund.")
            return None

        refund_request = RefundRequest(id=len(self.__orders) + 1, ticket=ticket, buyer=self)
        if refund_request.approve_refund():
            logging.info(f"Refund for ticket {ticket_id} approved.")
            return refund_request
        else:
            logging.error(f"Refund for ticket {ticket_id} failed.")
            return None

class Event:
    def __init__(self, id: int, name: str, date: datetime, organizer: EventOrganizer, hall: 'Hall'):
        self.__id = id
        self.__name = name
        self.__date = date
        self.__organizer = organizer
        self.__hall = hall
        self.__zones: Dict[str, 'Zone'] = {}

    # Getter for id
    @property
    def id(self):
        return self.__id

    # Getter and setter for name
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    # Getter for zones
    @property
    def zones(self):
        return self.__zones

    def add_zone(self, zone: 'Zone'):
        self.__zones[zone.type] = zone
        logging.info(f"Zone '{zone.type}' added to event '{self.name}'.")

    def add_zone_with_percentage(self, zone_type: str, percentage: float, price: float):
        """
        Add a zone with a percentage of the hall's capacity.
        :param zone_type: Type of the zone (e.g., "VIP", "Regular")
        :param percentage: Percentage of the hall's capacity (e.g., 0.2 for 20%)
        :param price: Price of tickets in this zone
        """
        capacity = int(self.__hall.capacity * percentage)
        zone = Zone(type=zone_type, capacity=capacity, price=price)
        self.add_zone(zone)
        logging.info(f"Zone '{zone_type}' added with {capacity} seats ({percentage * 100}% of hall capacity).")

class Hall:
    def __init__(self, id: int, size: str, capacity: int):
        self.__id = id
        self.__size = size
        self.__capacity = capacity

    # Getter for id
    @property
    def id(self):
        return self.__id

    # Getter and setter for size
    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value: str):
        self.__size = value

    # Getter and setter for capacity
    @property
    def capacity(self):
        return self.__capacity

    @capacity.setter
    def capacity(self, value: int):
        self.__capacity = value

class Zone:
    def __init__(self, type: str, capacity: int, price: float):
        self.__type = type
        self.__capacity = capacity
        self.__price = price
        self.__tickets: List['Ticket'] = [Ticket(id=i, zone=self) for i in range(1, capacity + 1)]

    # Getter for type
    @property
    def type(self):
        return self.__type

    # Getter for price
    @property
    def price(self):
        return self.__price

    # Getter for tickets
    @property
    def tickets(self):
        return self.__tickets

    def get_available_tickets(self, quantity: int) -> List['Ticket']:
        available_tickets = [ticket for ticket in self.__tickets if ticket.status == TicketStatus.AVAILABLE]
        return available_tickets[:quantity]

class Ticket:
    def __init__(self, id: int, zone: 'Zone'):
        self.__id = id
        self.__zone = zone
        self.__buyer: Optional[Buyer] = None
        self.__status = TicketStatus.AVAILABLE

    # Getter for id
    @property
    def id(self):
        return self.__id

    # Getter for zone
    @property
    def zone(self):
        return self.__zone

    # Getter for status
    @property
    def status(self):
        return self.__status

    # Setter for status
    @status.setter
    def status(self, value: TicketStatus):
        self.__status = value

    def purchase(self, buyer: Buyer) -> bool:
        if self.__status == TicketStatus.AVAILABLE:
            self.__buyer = buyer
            self.__status = TicketStatus.SOLD
            buyer.tickets.append(self)
            logging.info(f"Ticket {self.__id} purchased by {buyer.name}.")
            return True
        return False

    def refund(self) -> bool:
        if self.__status == TicketStatus.SOLD and self.__buyer:
            self.__status = TicketStatus.REFUNDED
            logging.info(f"Ticket {self.__id} refunded.")
            return True
        return False

class Order:
    def __init__(self, id: int, buyer: Buyer):
        self.__id = id
        self.__buyer = buyer
        self.__tickets: List[Ticket] = []
        self.__total_price: float = 0.0
        self.__status = OrderStatus.PENDING

    # Getter for id
    @property
    def id(self):
        return self.__id

    # Getter for status
    @property
    def status(self):
        return self.__status

    def add_ticket(self, ticket: Ticket):
        self.__tickets.append(ticket)
        self.__total_price += ticket.zone.price  # ใช้ getter ของ price

    def complete_order(self) -> bool:
        if self.__status == OrderStatus.PENDING:
            self.__status = OrderStatus.COMPLETED
            payment = Payment(id=len(self.__buyer.orders) + 1, order=self, amount=self.__total_price)
            if payment.process_payment(success=True):
                self.__buyer.orders.append(self)
                logging.info(f"Order {self.__id} completed successfully.")
                return True
            else:
                self.__status = OrderStatus.PENDING
                logging.error(f"Payment for order {self.__id} failed.")
                return False
        return False

    def cancel_order(self) -> bool:
        if self.__status == OrderStatus.PENDING:
            self.__status = OrderStatus.CANCELED
            for ticket in self.__tickets:
                ticket.status = TicketStatus.AVAILABLE
            logging.info(f"Order {self.__id} canceled.")
            return True
        return False

class Payment:
    def __init__(self, id: int, order: Order, amount: float):
        self.__id = id
        self.__order = order
        self.__amount = amount
        self.__status = PaymentStatus.PENDING

    # Getter for status
    @property
    def status(self):
        return self.__status

    def process_payment(self, success: bool) -> bool:
        if success:
            self.__status = PaymentStatus.COMPLETED
            logging.info(f"Payment {self.__id} completed successfully.")
            return True
        else:
            self.__status = PaymentStatus.FAILED
            logging.error(f"Payment {self.__id} failed.")
            return False

class RefundRequest:
    def __init__(self, id: int, ticket: Ticket, buyer: Buyer):
        self.__id = id
        self.__ticket = ticket
        self.__buyer = buyer
        self.__status = RefundStatus.PENDING
        self.__refund_amount = ticket.zone.price

    # Getter for status
    @property
    def status(self):
        return self.__status

    def approve_refund(self) -> bool:
        if self.__status == RefundStatus.PENDING:
            self.__status = RefundStatus.APPROVED
            self.__ticket.refund()
            logging.info(f"Refund request {self.__id} approved.")
            return True
        return False

    def reject_refund(self) -> bool:
        if self.__status == RefundStatus.PENDING:
            self.__status = RefundStatus.REJECTED
            logging.info(f"Refund request {self.__id} rejected.")
            return True
        return False

# Test Functions
def test_event_creation():
    organizer = EventOrganizer(id=1, name="John Doe", email="john@example.com", role="Organizer")
    hall = Hall(id=1, size="Large", capacity=1000)
    event = organizer.create_event(event_id=1, name="Concert", date=datetime.now(), hall=hall)
    assert event.name == "Concert"
    assert len(organizer.events) == 1
    print("Event creation test passed!")

def test_ticket_purchase():
    organizer = EventOrganizer(id=1, name="John Doe", email="john@example.com", role="Organizer")
    hall = Hall(id=1, size="Large", capacity=1000)
    event = organizer.create_event(event_id=1, name="Concert", date=datetime.now(), hall=hall)

    # Add VIP zone (20% of hall capacity)
    event.add_zone_with_percentage(zone_type="VIP", percentage=0.2, price=150.0)

    # Add Regular zone (80% of hall capacity)
    event.add_zone_with_percentage(zone_type="Regular", percentage=0.8, price=50.0)

    buyer = Buyer(id=2, name="Jane Doe", email="jane@example.com", role="Buyer")
    order = buyer.purchase_tickets(event, zone_type="VIP", quantity=2)
    assert order is not None
    assert len(buyer.tickets) == 2
    assert buyer.tickets[0].status == TicketStatus.SOLD
    print("Ticket purchase test passed!")

def test_refund_request():
    organizer = EventOrganizer(id=1, name="John Doe", email="john@example.com", role="Organizer")
    hall = Hall(id=1, size="Large", capacity=1000)
    event = organizer.create_event(event_id=1, name="Concert", date=datetime.now(), hall=hall)

    # Add VIP zone (20% of hall capacity)
    event.add_zone_with_percentage(zone_type="VIP", percentage=0.2, price=150.0)

    # Add Regular zone (80% of hall capacity)
    event.add_zone_with_percentage(zone_type="Regular", percentage=0.8, price=50.0)

    buyer = Buyer(id=2, name="Jane Doe", email="jane@example.com", role="Buyer")
    order = buyer.purchase_tickets(event, zone_type="VIP", quantity=2)
    refund_request = buyer.request_refund(ticket_id=buyer.tickets[0].id)
    assert refund_request is not None
    assert refund_request.status == RefundStatus.APPROVED
    assert buyer.tickets[0].status == TicketStatus.REFUNDED
    print("Refund request test passed!")

# Run tests
if __name__ == "__main__":
    test_event_creation()
    test_ticket_purchase()
    test_refund_request()