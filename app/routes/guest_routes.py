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

    # Fetch the deluxe room details
    room = Room.query.filter_by(room_number='Deluxe', is_available=True).first()

    if not room:
        flash("Sorry, the Deluxe Room is not available at the moment.", "danger")
        return render_template('guest/room-booking.html')  # Re-render the page instead of redirecting

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        checkin_date = request.form.get('checkin_date')
        checkout_date = request.form.get('checkout_date')
        adults = request.form.get('adults')
        children = request.form.get('children', 0)
        special_requests = request.form.get('special_requests', '')

        try:
            checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d")

            if checkout_date <= checkin_date:
                flash("Checkout date must be after check-in date!", "danger")
                return render_template('guest/room-booking.html', room=room)  # Re-render with error message

            # Step 3: Check if the guest already exists
            guest = Guest.query.filter_by(email=email).first()
            if not guest:
                guest = Guest(name=name, email=email, phone='N/A')  # Update phone if needed
                db.session.add(guest)
                db.session.commit()

            # Step 4: Create a new booking
            total_nights = (checkout_date - checkin_date).days
            total_price = total_nights * room.price

            new_booking = Booking(
                guest_id=guest.id,
                room_id=room.id,
                check_in_date=checkin_date,
                check_out_date=checkout_date,
                total_price=total_price,
                status=BookingStatus.PENDING,
                number_of_guests=int(adults) + int(children),
                special_requests=special_requests
            )
            db.session.add(new_booking)
            db.session.commit()

            # Step 5: Redirect to review page after booking is persisted
            return redirect(url_for('guest.review_room_booking_details', booking_id=new_booking.id))

        except Exception as e:
            print(f"Error processing booking: {e}")
            flash("There was an issue processing your booking.", "danger")
            return render_template('guest/room-booking.html', room=room)  # Re-render on error

    return render_template('guest/room-booking.html', room=room)


@guest_bp.route('/review-room-booking-details/<int:booking_id>', methods=['GET', 'POST'])
def review_room_booking_details(booking_id):
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
