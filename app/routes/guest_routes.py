from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Guest, Room, Booking, BookingStatus
from config import db
from datetime import datetime

guest_bp = Blueprint('guest', __name__, template_folder='../templates')


@guest_bp.route('/')
def index():
    return render_template('guest/index.html')

@guest_bp.route('/about')
def about():
    return render_template('guest/about.html')

@guest_bp.route('/contact')
def contact():
    return render_template('guest/contact.html')

@guest_bp.route('/deluxe-room')
def deluxe_room():
    return render_template('guest/deluxe.html')

@guest_bp.route('/executive-room')
def executive_room():
    return render_template('guest/executive.html')

@guest_bp.route('/standard-room')
def standard_room():
    return render_template('guest/standard-room-details.html')

@guest_bp.route('/hotel')
def hotel():
    return render_template('guest/hotel.html')

@guest_bp.route('/meetings-events')
def meetings_events():
    return render_template('guest/meetings-events.html')

@guest_bp.route('/reservation')
def reservation():
    return render_template('guest/reservation.html')


# Logic for room booking
@guest_bp.route('/room-booking-info', methods=['GET', 'POST'])
def room_booking():

    return render_template('guest/room-booking.html')


@guest_bp.route('/review-room-booking-details', methods=['GET', 'POST'])
def review_room_booking_details():
    if request.method == 'POST':
        # Handle form submission logic here
        pass
    return render_template('guest/review-room-booking.html')


@guest_bp.route('/payment', methods=['GET', 'POST'])
def process_payment():
    if request.method == 'POST':
        # Handle form submission logic here
        pass
    return render_template('guest/payment.html')


# Table Reservation Routes
@guest_bp.route('/table-reservation', methods=['GET', 'POST'])
def table_reservation():
    if request.method == 'POST':
        # Handle form submission logic here
        pass
    return render_template('guest/table-reservation.html')


@guest_bp.route('/confirm-table-reservation', methods=['GET', 'POST'])
def confirm_table_reservation():
    if request.method == 'POST':
        # Skip database logic for testing
        return redirect(url_for('guest.success_table_reservation'))
    return render_template('guest/confirm-table-reservation.html')

@guest_bp.route('/success-table-reservation', methods=['GET'])
def success_table_reservation():
    return render_template('guest/success-table-reservation.html')
