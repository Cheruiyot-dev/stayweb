from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Guest, Room, Booking, BookingStatus, RoomCategory, Payment, PaymentMethod
from config import db
from datetime import datetime
import re
from sqlalchemy import or_
import random

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



@guest_bp.route('/room-booking', methods=['GET', 'POST'])
def room_booking():
    room_categories = RoomCategory.query.all()
    if request.method == 'POST':
       
       
        try:
            # Retrieve form data
            name = request.form.get('name', '').strip()
            # print(name)
            email = request.form.get('email', '').strip()
            checkin_date = request.form.get('checkin_date')
            checkout_date = request.form.get('checkout_date')
            adults = int(request.form.get('adults', 1))
            children = int(request.form.get('children', 0))
            special_requests = request.form.get('special_requests', '').strip()
            room_category_id = int(request.form.get('room_category'))
            

            # Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Invalid email address.", "danger")
                return render_template('guest/room-booking.html', room_categories=room_categories)

            # Validate dates
            try:
                checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
                checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").date()
                if checkout_date <= checkin_date:
                    raise ValueError("Checkout date must be after check-in date.")
            except ValueError as e:
                flash(str(e), "danger")
                return render_template('guest/room-booking.html', room_categories=room_categories)

            # Validate room category
            room_category = RoomCategory.query.get(room_category_id)
            # print(type(room_category))
     
            if not room_category:
                flash("Invalid room category selected.", "danger")
                return render_template('guest/room-booking.html', room_categories=room_categories)

            # Find available room
            available_room = Room.query.filter_by(category_id=room_category_id, is_available=True).first()
            print(type(available_room))

            available_room_dict = {
                        'id': available_room.id,
                        'room_number': available_room.room_number,
                        'category_id': available_room.category_id,
                        'price': float(available_room.price),
                        'is_available': available_room.is_available,
                        'description': available_room.description,
                        'floor': available_room.floor,
                        'created_at': available_room.created_at,
                        'updated_at': available_room.updated_at
                    }
            
            
            # print(available_room_dict)

            if not available_room:
                flash(f"No {room_category.name} rooms are available.", "danger")
                return render_template('guest/room-booking.html', room_categories=room_categories)

            # Validate guest count
            total_guests = adults + children
            if total_guests <= 0:
                flash("Number of guests must be at least 1.", "danger")
                return render_template('guest/room-booking.html', room_categories=room_categories)

            # Get or create guest
            # Filter guest by email or name
            # check if guest already exists in db. If not, create a new user and persist in db.
            # Then proceed to make the booking
            # First check guest. 
            # if guest: 
# Check if the guest exists
            guest = Guest.query.filter(or_(Guest.email == email, Guest.name == name)).first()

            if guest:
                print("Guest with email exists:", guest)

                if guest.name != name:
                    guest.name = name
                    db.session.commit()
                    print("Guest's name updated")

            else:
                guest = Guest(name=name, email=email, phone='N/A')
                db.session.add(guest)
                db.session.commit()
                print("New guest created:", guest)


            # Calculate total price
            total_nights = (checkout_date - checkin_date).days
            total_price = total_nights * available_room.price

            # Create new booking
            new_booking = Booking(
                guest=guest,
                room=available_room,
                check_in_date=checkin_date,
                check_out_date=checkout_date,
                total_price=total_price,
                status=BookingStatus.PENDING,
                number_of_guests=total_guests,
                special_requests=special_requests
            )

            db.session.add(new_booking)
            db.session.commit()

            flash("Your booking has been successfully submitted!", "success")
            return redirect(url_for('guest.confirm_room_booking', booking_id=new_booking.id))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while processing your booking: {str(e)}", "danger")

    return render_template('guest/room-booking.html', room_categories=room_categories)

@guest_bp.route('/confirm-booking/<int:booking_id>')
def confirm_room_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('guest/confirm_room_booking.html', booking=booking)


@guest_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def process_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        print("...paymethod...........", payment_method)

        # Validate payment method
        if payment_method == 'card':
            card_name = request.form.get('card_name')
            card_number = request.form.get('card_number')
            expiry_month = request.form.get('expiry_month')
            expiry_year = request.form.get('expiry_year')
            cvv = request.form.get('cvv')

            # Perform validation and payment processing (simulated here)
            if not all([card_name, card_number, expiry_month, expiry_year, cvv]):
                flash('Please fill in all the card details correctly.', 'danger')
                return render_template('guest/payment.html', booking=booking)

            
            # Assume payment is successful
            new_payment = Payment(
                booking_id=booking_id,
                amount=booking.total_price,
                payment_method=PaymentMethod.CREDIT_CARD,
                transaction_id='CARD' + str(random.randint(10000, 99999)),
                is_successful=True,
                payment_date=datetime.utcnow(),
                card_last_four=card_number[-4:]
            )
   
        elif payment_method == 'mpesa':
            mpesa_phone = request.form.get('phone')
            print(mpesa_phone)

            if not mpesa_phone:
                flash('Please provide a valid M-Pesa phone number.', 'danger')
                return render_template('guest/payment.html', booking=booking)
            
            # Simulate successful M-Pesa payment
            new_payment = Payment(
                booking_id=booking_id,
                amount=booking.total_price,
                payment_method=PaymentMethod.CASH,  
                transaction_id='MPESA' + str(random.randint(10000, 99999)),
                is_successful=True,
                payment_date=datetime.utcnow()
            )

        else:
            flash('Invalid payment method.', 'danger')
            return render_template('guest/payment.html', booking=booking)
        
        db.session.add(new_payment)
        booking.status = BookingStatus.CONFIRMED
        db.session.commit() 

        flash('Payment was successful!', 'success')
        return redirect(url_for('guest.payment_success', booking_id=booking_id))  
                
    return render_template('guest/payment.html', booking=booking)

@guest_bp.route('/payment-success/<int:booking_id>', methods=['GET'])
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('guest/success_payment.html', booking=booking)

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
