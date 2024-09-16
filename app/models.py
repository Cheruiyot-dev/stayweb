from config import db
from sqlalchemy.orm import validates
from datetime import datetime
from enum import Enum
import re

# Guest Model
class Guest(db.Model):
    __tablename__ = 'guests'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # Relationships
    bookings = db.relationship('Booking', back_populates='guest', lazy='select', cascade='all, delete-orphan')
    table_reservations = db.relationship('TableReservation', back_populates='guest', lazy='select', cascade='all, delete-orphan')

    # Email Validation
    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        return email

    def __repr__(self):
        return f'<Guest {self.name}>'

# Room Category Model
class RoomCategory(db.Model):
    __tablename__ = 'room_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<RoomCategory {self.name}>'

# Room Model
class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('room_categories.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text)
    floor = db.Column(db.Integer, nullable=False)

    # Relationships
    category = db.relationship('RoomCategory', backref=db.backref('rooms', lazy='select'))
    bookings = db.relationship('Booking', back_populates='room', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Room {self.room_number} - {self.category.name}>'

# Booking Status Enum
class BookingStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'
    CANCELLED = 'cancelled'

# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)

    # Relationships
    guest = db.relationship('Guest', back_populates='bookings')
    room = db.relationship('Room', back_populates='bookings')
    payments = db.relationship('Payment', back_populates='booking', cascade='all, delete-orphan')

    # Check-out Date Validation
    @validates('check_out_date')
    def validate_check_out_date(self, key, check_out_date):
        if check_out_date <= self.check_in_date:
            raise ValueError("Check-out date must be after check-in date")
        return check_out_date

    def __repr__(self):
        return f'<Booking {self.id} - Room {self.room.room_number} - Guest {self.guest.name}>'

# Table Model
class Table(db.Model):
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    table_number = db.Column(db.String(10), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    reservations = db.relationship('TableReservation', back_populates='table', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Table {self.table_number} - Capacity: {self.capacity}>'

# Table Reservation Model
class TableReservation(db.Model):
    __tablename__ = 'table_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    
    reservation_date = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    special_requests = db.Column(db.Text)

    # Relationships
    table = db.relationship('Table', back_populates='reservations')
    guest = db.relationship('Guest', back_populates='table_reservations')

    # Number of Guests Validation
    @validates('number_of_guests')
    def validate_number_of_guests(self, key, number_of_guests):
        if number_of_guests > self.table.capacity:
            raise ValueError("Number of guests exceeds table capacity")
        return number_of_guests

    def __repr__(self):
        return f'<TableReservation {self.id} - Table {self.table.table_number} - Guest {self.guest.name}>'

# Payment Method Enum
class PaymentMethod(Enum):
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'

# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    is_successful = db.Column(db.Boolean, default=True, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    card_last_four = db.Column(db.String(4))
    notes = db.Column(db.Text)

    # Relationships
    booking = db.relationship('Booking', back_populates='payments')

    # Validate last four digits of the card
    @validates('card_last_four')
    def validate_card_last_four(self, key, card_last_four):
        if card_last_four and (len(card_last_four) != 4 or not card_last_four.isdigit()):
            raise ValueError("Card last four must be exactly 4 digits")
        return card_last_four

    def __repr__(self):
        return f'<Payment {self.id} - Booking {self.booking_id} - Amount: {self.amount} - Date: {self.payment_date}>'
