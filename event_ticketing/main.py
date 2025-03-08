from datetime import datetime
from enum import Enum

# Enum for ticket status
class TicketStatus(Enum):
    AVAILABLE = "Available"
    SOLD = "Sold"
    REFUNDED = "Refunded"

# Enum for refund request status
class RefundStatus(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

# Enum for payment status
class PaymentStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

# Class to represent a ticket zone (VIP or Regular)
class Zone:
    def __init__(self, id, type, capacity, price):
        self.id = id
        self.type = type  # VIP or Regular
        self.capacity = capacity
        self.price = price
        self.tickets = [Ticket(id=i, zone=self) for i in range(capacity)]  # Create tickets for the zone

# Class to represent a ticket
class Ticket:
    def __init__(self, id, zone):
        self.id = id
        self.zone = zone
        self.status = TicketStatus.AVAILABLE  # Initially available
        self.buyer = None  # No buyer initially

    def purchase(self, buyer):
        if self.status == TicketStatus.AVAILABLE:
            self.status = TicketStatus.SOLD
            self.buyer = buyer
            print(f"Ticket {self.id} purchased by {buyer.name}")
        else:
            print(f"Ticket {self.id} is not available for purchase.")

    def refund(self):
        if self.status == TicketStatus.SOLD:
            self.status = TicketStatus.REFUNDED
            print(f"Ticket {self.id} refunded.")
        else:
            print(f"Ticket {self.id} cannot be refunded as it is not sold.")

# Class to represent a hall (small, medium, large)
class Hall:
    def __init__(self, id, size, capacity):
        self.id = id
        self.size = size
        self.capacity = capacity
        self.zones = []  # Different zones in the hall (VIP, Regular)

    def add_zone(self, zone):
        self.zones.append(zone)

# Class to represent an event
class Event:
    def __init__(self, id, name, date, organizer, hall):
        self.id = id
        self.name = name
        self.date = date
        self.organizer = organizer
        self.hall = hall

# Class to represent a buyer
class Buyer:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.tickets = []

    def view_tickets(self, event):
        available_tickets = []
        
        for zone in event.hall.zones:
            available_tickets.extend([ticket for ticket in zone.tickets if ticket.status == TicketStatus.AVAILABLE])
        
        if not available_tickets:
            print(f"Sorry, there are no tickets left for {event.name}.")
        
        return available_tickets
    
    def purchase(self, ticket):
        if ticket.status == TicketStatus.AVAILABLE:
            ticket.purchase(self)
            self.tickets.append(ticket)  # Add the purchased ticket to the buyer's list
        else:
            print(f"Ticket {ticket.id} is not available for purchase.")

# Class to represent a payment
class Payment:
    def __init__(self, id, buyer, ticket, amount, status=PaymentStatus.PENDING):
        self.id = id
        self.buyer = buyer
        self.ticket = ticket
        self.amount = amount
        self.status = status

    def process_payment(self):
        if self.status == PaymentStatus.PENDING:
            self.status = PaymentStatus.COMPLETED
            print(f"Payment for Ticket {self.ticket.id} completed.")
        else:
            print(f"Payment for Ticket {self.ticket.id} has already been processed.")

# Class to represent a refund request
class RefundRequest:
    def __init__(self, ticket, buyer, refund_amount, status=RefundStatus.PENDING):
        self.ticket = ticket
        self.buyer = buyer
        self.refund_amount = refund_amount
        self.status = status

    def approve_refund(self):
        if self.ticket.status == TicketStatus.SOLD:
            self.status = RefundStatus.APPROVED
            self.ticket.refund()  # Refund the ticket
            print(f"Refund for Ticket {self.ticket.id} approved for {self.buyer.name}.")
        else:
            self.status = RefundStatus.REJECTED
            print(f"Refund for Ticket {self.ticket.id} rejected. Ticket not sold.")

# Testing all scenarios including no tickets left, purchasing, and refund requests
def test_all_hall_sizes():
    # Create buyers
    buyer1 = Buyer(id=1, name="Alice", email="alice@example.com")
    buyer2 = Buyer(id=2, name="Bob", email="bob@example.com")
    
    # Create halls of different sizes
    small_hall = Hall(id=1, size="Small", capacity=300)
    medium_hall = Hall(id=2, size="Medium", capacity=600)
    large_hall = Hall(id=3, size="Large", capacity=1200)

    # Create zones with available tickets for each hall
    small_hall.add_zone(Zone(id=1, type="VIP", capacity=50, price=50.0))
    small_hall.add_zone(Zone(id=2, type="Regular", capacity=250, price=30.0))

    medium_hall.add_zone(Zone(id=1, type="VIP", capacity=150, price=50.0))
    medium_hall.add_zone(Zone(id=2, type="Regular", capacity=450, price=30.0))

    large_hall.add_zone(Zone(id=1, type="VIP", capacity=250, price=50.0))
    large_hall.add_zone(Zone(id=2, type="Regular", capacity=950, price=30.0))

    # Create events for each hall
    event_small = Event(id=1, name="Small Hall Event", date=datetime(2025, 5, 10), organizer=None, hall=small_hall)
    event_medium = Event(id=2, name="Medium Hall Event", date=datetime(2025, 5, 11), organizer=None, hall=medium_hall)
    event_large = Event(id=3, name="Large Hall Event", date=datetime(2025, 5, 12), organizer=None, hall=large_hall)

    # Simulate buying tickets
    print(f"Testing Small Hall ({small_hall.size}):")
    available_tickets_small = buyer1.view_tickets(event_small)
    if available_tickets_small:
        ticket_small = available_tickets_small[0]
        ticket_small.purchase(buyer1)
    else:
        print("No tickets are available for purchase.")
    
    # Buyer 2 views available tickets for Medium Hall Event
    print(f"\nTesting Medium Hall ({medium_hall.size}):")
    available_tickets_medium = buyer2.view_tickets(event_medium)
    if available_tickets_medium:
        ticket_medium = available_tickets_medium[0]
        ticket_medium.purchase(buyer2)
    else:
        print("No tickets are available for purchase.")
    
    # Buyer 1 views available tickets for Large Hall Event
    print(f"\nTesting Large Hall ({large_hall.size}):")
    available_tickets_large = buyer1.view_tickets(event_large)
    if available_tickets_large:
        ticket_large = available_tickets_large[0]
        ticket_large.purchase(buyer1)
    else:
        print("No tickets are available for purchase.")
    
    # Simulate refund request for Medium Hall ticket
    print(f"\nRefunding ticket for Medium Hall purchased by {buyer2.name}:")
    refund_request = RefundRequest(ticket_medium, buyer2, ticket_medium.zone.price)
    refund_request.approve_refund()

# Run the test for all hall sizes
test_all_hall_sizes()
