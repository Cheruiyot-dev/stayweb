from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Guest, Room, Booking, BookingStatus, RoomCategory, Payment, PaymentMethod, TableReservation
from config import db
from datetime import datetime
import re
from sqlalchemy import or_
import random

guest_bp = Blueprint('guest', __name__, template_folder='../templates')


@guest_bp.route('/')
def index():
    return render_template('guest/index.html')


@guest_bp.route('/gallery')
def gallery():
    return render_template('guest/gallery.html')

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
            print(name)
            email = request.form.get('email', '').strip()
            checkin_date = request.form.get('checkin_date')
            checkout_date = request.form.get('checkout_date')
            adults = int(request.form.get('adults', 1))
            children = int(request.form.get('children', 0))
            special_requests = request.form.get('special_requests', '').strip()
            room_category_id = int(request.form.get('room_category'))
            print("fywfgyw",room_category_id)
            

            # Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Invalid email address.", "danger")
                return render_template('guest/room-booking.html',
                                       room_categories=room_categories)

            # Validate dates
            try:
                checkin_date = datetime.strptime(checkin_date,
                                                 "%Y-%m-%d").date()
                print("Checkindate is", checkin_date)
                checkout_date = datetime.strptime(checkout_date,
                                                  "%Y-%m-%d").date()
                if checkout_date <= checkin_date:
                    raise ValueError("Checkout date must be after check-in date.")
            except ValueError as e:
                flash(str(e), "danger")
                return render_template('guest/room-booking.html',
                                       room_categories=room_categories)

            # Validate room category
            room_category = RoomCategory.query.get(room_category_id)
            # print(type(room_category))
   
            if not room_category:
                flash("Invalid room category selected.", "danger")
                return render_template('guest/room-booking.html',
                                       room_categories=room_categories)

            # Find available room
            available_room = Room.query.filter_by(category_id=room_category_id,
                                                  is_available=True).first()
            print(type(available_room))
            print("available room price is:", available_room.price)
    
            # print(available_room_dict)

            if not available_room:
                flash(f"No {room_category.name} rooms are available.", "danger")
                return render_template('guest/room-booking.html',
                                       room_categories=room_categories)

            
         # Calculate total price
        
            total_nights = (checkout_date - checkin_date).days
            print("total nights are:", total_nights)
            total_price = total_nights * available_room.price
            print("total price is:", total_price)

         # Store booking information in session 

            session['booking_info'] = {
                'name': name,
                'email': email,
                'checkin_date': checkin_date.isoformat(),
                'checkout_date': checkout_date.isoformat(),
                'adults': adults,
                'children': children,
                'special_requests': special_requests,
                'room_id': available_room.id,
                'total_price': float(total_price),
                'total_guests': adults + children,
                'room_category': room_category.name
            }

            # print("Session is:", session)
            print("Redirecting to confirm booking page")

            return redirect(url_for('guest.confirm_room_booking'))
     
        except Exception as e:
            flash(f"An error occurred while processing your booking: {str(e)}",
                  "danger")

    return render_template('guest/room-booking.html',
                           room_categories=room_categories)

@guest_bp.route('/confirm-booking', methods=['GET', 'POST'])
def confirm_room_booking():
    booking_info = session.get('booking_info')
    if not booking_info:
        flash("No booking information found. Please make a booking.", 'danger')
        return redirect(url_for('guest.room_booking'))
    
    if request.method == 'POST':
        # user confirms payment
        return redirect(url_for('guest.process_payment'))
    return render_template('guest/confirm_room_booking.html', booking_info=booking_info)


@guest_bp.route('/payment', methods=['GET', 'POST'])
def process_payment():
    booking_info = session.get('booking_info')
    print(booking_info)
    if not booking_info:
        flash('No booking information found. Please starta anew booking.', 'danger')
        return redirect(url_for('guest.room_booking'))

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
                return render_template('guest/payment.html', booking_info=booking_info)

            
          # Simulate card payment processing here
            payment_successful = True  # In reality, this would be the result of processing the payment
            transaction_id = 'CARD' + str(random.randint(10000, 99999))
            payment_method_enum = PaymentMethod.CREDIT_CARD
            card_last_four = card_number[-4:]
   
        elif payment_method == 'mpesa':
            phone = request.form.get('phone')
            print(phone)

            if not phone:
                flash('Please provide a valid M-Pesa phone number.', 'danger')
                return render_template('guest/payment.html', booking_info=booking_info)
            
            # Simulating M-Pesa payment processing here
            payment_successful = True  # In reality, this would be the result of processing the payment
            transaction_id = 'MPESA' + str(random.randint(10000, 99999))
            payment_method_enum = PaymentMethod.CASH
            card_last_four = None


        else:
            flash('Invalid payment method.', 'danger')
            return render_template('guest/payment.html', booking_info=booking_info)
        
        if payment_successful:
            # create or update guest
            guest = Guest.query.filter(or_(Guest.email == booking_info['email'], Guest.name == booking_info['name'])).first()
            if not guest:
                guest = Guest(name=booking_info['name'], email=booking_info['email'], phone='N/A')
                db.session.add(guest)
            elif guest.name != booking_info['name']:
                guest.name = booking_info['name']

            # Create booking
            new_booking = Booking(
                guest=guest,
                room_id=booking_info['room_id'],
                check_in_date=datetime.fromisoformat(booking_info['checkin_date']),
                check_out_date=datetime.fromisoformat(booking_info['checkout_date']),
                total_price=booking_info['total_price'],
                status=BookingStatus.CONFIRMED,
                number_of_guests=booking_info['total_guests'],
                special_requests=booking_info['special_requests']
            )
            db.session.add(new_booking)


            # Create payment record
            new_payment = Payment(
                booking=new_booking,
                amount=booking_info['total_price'],
                payment_method=payment_method_enum,
                transaction_id=transaction_id,
                is_successful=True,
                payment_date=datetime.utcnow(),
                card_last_four=card_last_four
            )
            db.session.add(new_payment)

            db.session.commit()

            # Clear the booking information from the session
            session.pop('booking_info', None)

            flash('Payment was successful. Your booking is confirmed!', 'success')
            return redirect(url_for('guest.payment_success', booking_id=new_booking.id))
        else:
            flash('Payment processing failed.Please try again.', 'danger')
                
    return render_template('guest/payment.html', booking_info=booking_info)

@guest_bp.route('/payment-success/<int:booking_id>', methods=['GET'])
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('guest/success_payment.html', booking=booking)

# Table Reservation Routes
@guest_bp.route('/table-reservation', methods=['GET', 'POST'])
def table_reservation():
    if request.method == 'POST':
        # Handle form submission logic here
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        reservation_date = request.form.get('reservation_date')
        reservation_time = request.form.get('reservation_time')
        number_of_people = request.form.get('number_of_people')
        special_requests = request.form.get('special_requests')

        
        print(f"Special requests: {special_requests}")

        # Validate form data
        if not all([full_name, email, phone_number, reservation_date, reservation_time, number_of_people]):
            flash('All fields are required.', 'danger')
            return render_template('guest/table-reservation.html')

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.", "danger")
            return render_template('guest/table-reservation.html')
        
       
        # Convert date and time strings to datetime object
        try:
            reservation_datetime = datetime.strptime(f'{reservation_date} {reservation_time}', '%Y-%m-%d %H:%M')
        except ValueError as ve:
            flash(f'Invalid date or time format: {str(ve)}', 'danger')
            return render_template('guest/table-reservation.html')
        
        number_of_people = int(number_of_people)
            
         # Check if reservation is in the future
        if reservation_datetime <= datetime.now():
            flash("Reservation must be for a future date and time.", "danger")
            return render_template('guest/table-reservation.html')

         

  

        try:    

            table_reservation = TableReservation(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                reservation_date=reservation_datetime,
                number_of_guests=number_of_people,
                special_requests=special_requests
            )

            # Add and commit the reservation to the database
            db.session.add(table_reservation)
            db.session.commit()
            print("reservation created")

         

            # Notify the user of successful reservation
            flash('Your table reservation has been confirmed!', 'success')
            return redirect(url_for('guest.success_table_reservation'))

        except Exception as e:
            # Rollback the session if any error occurs
            db.session.rollback()
            print(f"Error occurred: {str(e)}")
            flash(f'An error occurred while processing your reservation: {str(e)}', 'danger')
            return redirect(url_for('guest.table_reservation'))
    return render_template('guest/table-reservation.html')                


# @guest_bp.route('/confirm-table-reservation', methods=['GET', 'POST'])
# def confirm_table_reservation():
#     table_reservation_info = session.get('table_reservation_info')
#     print(type(table_reservation_info))
#     print("Table infor is:", table_reservation_info)

#     if not table_reservation_info:
#         flash("No table reservation information available.\
#               Please make a reservation first.", 'danger')
#         return redirect(url_for('guest.table_reservation')) 
#     if request.method == 'POST':
#         try:
#             # Extract reservation info from session
#             full_name = table_reservation_info['full_name']
#             email = table_reservation_info['email']
#             phone_number = table_reservation_info['phone_number']
#             reservation_date = table_reservation_info['reservation_date']
#             reservation_time = table_reservation_info['reservation_time']
#             number_of_people = table_reservation_info['number_of_people']
#             special_requests = table_reservation_info.get('special_requests', '')

#             print("name is:", full_name)


@guest_bp.route('/success-table-reservation', methods=['GET'])
def success_table_reservation():
   
   
    return render_template('guest/success-table-reservation.html')
