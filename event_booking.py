import sqlite3
import threading
from abc import ABC, abstractmethod

# Abstract class for events
class AbstractEvent(ABC):
    @abstractmethod
    def event_info(self):
        pass

# Event class inheriting AbstractEvent
class Event(AbstractEvent):
    def __init__(self, name, description, organizer):
        self.name = name
        self.description = description
        self.organizer = organizer

    def event_info(self):
        return f"{self.name} by {self.organizer}: {self.description}"

# User class
class User:
    def __init__(self, name, contact):
        self.name = name
        self.contact = contact

# TicketBooking class
class TicketBooking:
    def __init__(self, event, date, user, price):
        self.event = event
        self.date = date
        self.user = user
        self.price = price

# BookingManager class
class BookingManager:
    def __init__(self):
        self.bookings = []

    def add_booking(self, booking):
        self.bookings.append(booking)

    def filter_bookings_by_event(self, event_name):
        return list(filter(lambda b: b.event.name == event_name, self.bookings))

    def save_to_db(self):
        def db_thread():
            try:
                conn = sqlite3.connect("bookings.db")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        event_name TEXT,
                        date TEXT,
                        customer_name TEXT,
                        price REAL
                    )
                """)
                for booking in self.bookings:
                    cursor.execute("""
                        INSERT INTO bookings (event_name, date, customer_name, price)
                        VALUES (?, ?, ?, ?)
                    """, (booking.event.name, booking.date, booking.user.name, booking.price))
                conn.commit()
                conn.close()
                print("Bookings saved to database.")
            except Exception as e:
                print(f"Error saving to database: {e}")

        threading.Thread(target=db_thread).start()

    def save_to_file(self):
        try:
            with open("bookings.txt", "w") as f:
                for booking in self.bookings:
                    f.write(f"{booking.event.name},{booking.date},{booking.user.name},{booking.price}\n")
            print("Bookings saved to file.")
        except Exception as e:
            print(f"Error writing to file: {e}")

# Custom exception for booking errors
class BookingException(Exception):
    pass

# Main program
def main():
    try:
        # Input events
        events = []
        num_events = int(input("Enter the number of events: "))
        for _ in range(num_events):
            name, description, organizer = input().split(",")
            events.append(Event(name, description, organizer))

        # Input users
        users = []
        num_users = int(input("Enter the number of users: "))
        for _ in range(num_users):
            name, contact = input().split(",")
            users.append(User(name, contact))

        # Input bookings
        manager = BookingManager()
        num_bookings = int(input("Enter the number of bookings: "))
        for _ in range(num_bookings):
            event_name, date, user_name, price = input().split(",")
            event = next((e for e in events if e.name == event_name), None)
            user = next((u for u in users if u.name == user_name), None)
            if not event or not user:
                raise BookingException("Invalid event or user.")
            manager.add_booking(TicketBooking(event, date, user, float(price)))

        # Save bookings in a thread
        print("Processing bookings in a separate thread...")
        manager.save_to_db()
        manager.save_to_file()

        # Filter bookings by event name
        search_event = input("Enter the event name to be searched: ")
        filtered_bookings = manager.filter_bookings_by_event(search_event)

        # Output bookings
        print(f"Bookings for {search_event}")
        print(f"{'Event Name':<15}{'Booking Time':<15}{'Customer':<15}{'Price':<10}")
        for booking in filtered_bookings:
            print(f"{booking.event.name:<15}{booking.date:<15}{booking.user.name:<15}{booking.price:<10}")

    except BookingException as be:
        print(f"Booking error: {be}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
