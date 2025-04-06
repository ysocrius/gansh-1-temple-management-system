from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app as app, jsonify, send_file
from database import seva_list, user_collection, seva_collection
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import uuid
import secrets
import logging
import os
import razorpay
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

seva_bp = Blueprint("seva", __name__, url_prefix="/seva")

# Initialize Razorpay client
key_id = os.environ.get('key_id', 'rzp_test_6WWw11VMvM8MXw')
key_secret = os.environ.get('key_secret', '4akdtf9N66cjL36XOSNjXYBc')
razorpay_client = razorpay.Client(auth=(key_id, key_secret))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@seva_bp.route("/user_seva")
def seva_list_view():
    """Display the list of available sevas."""
    seva_types = ["Archanegalu", "Abhishekas", "Alankar", "Pooja/Vratha", "Utsava", "Homa - Kanika"]
    
    selected_type = request.args.get("type", "all")

    if selected_type == "all":
        sevas_data = list(seva_list.find())  
    else:
        sevas_data = list(seva_list.find({"seva_type": selected_type}))  

    # Convert ObjectId to string for rendering
    for seva in sevas_data:
        seva["_id"] = str(seva["_id"])

    return render_template("user/user_seva.html", sevas=sevas_data, seva_types=seva_types, selected_type=selected_type)

@seva_bp.route('/confirm_order/<seva_id>', methods=['GET', 'POST'])
def confirm_order(seva_id):
    """Handles Seva Confirmation & Booking"""
    if 'user' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('user.login'))

    try:
        # Check if user session has the expected structure
        if not isinstance(session["user"], dict) or "id" not in session["user"]:
            flash("Session error. Please log out and log in again.", "warning")
            logger.error(f"User session missing ID. Session user data: {session.get('user')}")
            return redirect(url_for('user.login'))
            
        # Fetch user details
        user = user_collection.find_one({"_id": ObjectId(session["user"]["id"])})
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('user.login'))

        # First, check if this is an existing booking that needs payment
        try:
            existing_booking = seva_collection.find_one({
                "_id": ObjectId(seva_id),
                "user_id": session["user"]["id"],
                "status": "pending"
            })
            
            if existing_booking:
                # This is an existing booking, proceed to payment
                amount_in_paise = int(float(existing_booking["seva_price"]) * 100)
                order_data = {
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'receipt': f'seva_{str(existing_booking["_id"])}',
                    'notes': {
                        'seva_name': existing_booking["seva_name"],
                        'user_id': session["user"]["id"],
                        'booking_id': str(existing_booking["_id"])
                    }
                }
                
                # Create the order
                order = razorpay_client.order.create(order_data)
                
                # Render the payment page
                return render_template(
                    "user/seva_payment.html",
                    booking_id=str(existing_booking["_id"]),
                    seva={
                        "seva_name": existing_booking["seva_name"],
                        "seva_price": existing_booking["seva_price"],
                        "seva_type": existing_booking["seva_type"]
                    },
                    user=user,
                    key_id=key_id,
                    booking=existing_booking,
                    order_id=order['id']
                )
        except InvalidId:
            # Not a valid ObjectId, might be a new seva booking
            pass
            
        # If we're here, it's a new booking request - fetch seva details
        try:
            seva = seva_list.find_one({"_id": ObjectId(seva_id)})
            if not seva:
                flash("Seva not found.", "danger")
                return redirect(url_for('seva.seva_list_view'))
        except InvalidId:
            flash("Invalid Seva ID!", "danger")
            return redirect(url_for('seva.seva_list_view'))

        if request.method == 'POST':
            seva_date = request.form.get("seva_date")
            if not seva_date:
                flash("Please select a date!", "warning")
                return redirect(url_for('seva.confirm_order', seva_id=seva_id))

            # Create booking data
            booking_data = {
                "user_id": str(user["_id"]),
                "user_name": user["name"],
                "email": session["user"]["email"],
                "phone": user.get("phone", ""),
                "seva_id": str(seva["_id"]),
                "seva_name": seva["seva_name"],
                "seva_type": seva["seva_type"],
                "seva_price": seva["seva_price"],
                "seva_date": seva_date,
                "booking_date": datetime.now(),
                "status": "pending",
                "payment_status": "pending"
            }

            # Save to database
            try:
                result = seva_collection.insert_one(booking_data)
                if result.inserted_id:
                    # Create a Razorpay order
                    amount_in_paise = int(float(seva["seva_price"]) * 100)
                    order_data = {
                        'amount': amount_in_paise,
                        'currency': 'INR',
                        'receipt': f'seva_{str(result.inserted_id)}',
                        'notes': {
                            'seva_name': seva["seva_name"],
                            'user_id': session["user"]["id"],
                            'booking_id': str(result.inserted_id)
                        }
                    }
                    
                    # Create the order
                    order = razorpay_client.order.create(order_data)
                    
                    # Render the Razorpay checkout page
                    return render_template(
                        "user/seva_payment.html",
                        booking_id=str(result.inserted_id),
                        seva=seva,
                        user=user,
                        key_id=key_id,
                        booking=booking_data,
                        order_id=order['id']
                    )
                else:
                    flash("Failed to book seva. Please try again.", "danger")
            except Exception as e:
                flash(f"Error booking seva: {str(e)}", "danger")
                return redirect(url_for('seva.confirm_order', seva_id=seva_id))

        # GET request - show confirmation page
        today = datetime.now().strftime('%Y-%m-%d')
        return render_template(
            "user/confirm_booking.html",
            seva=seva,
            user=user,
            today=today
        )

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('seva.seva_list_view'))

@seva_bp.route('/create-razorpay-order/<booking_id>', methods=['POST'])
def create_razorpay_order(booking_id):
    """Create a Razorpay order for seva payment"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to continue'})
        
    try:
        booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'})
            
        # Create Razorpay order
        amount_in_paise = int(float(booking.get('seva_price', 0)) * 100)
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'seva_{booking_id}',
            'notes': {
                'seva_name': booking.get('seva_name', ''),
                'user_id': session['user']['id'],
                'booking_id': booking_id
            }
        }
        
        order = razorpay_client.order.create(order_data)
        
        return jsonify({
            'success': True,
            'data': {
                'order_id': order['id'],
                'amount': float(booking.get('seva_price', 0)),
                'currency': 'INR',
                'key_id': key_id
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@seva_bp.route('/verify-razorpay-payment', methods=['POST'])
def verify_razorpay_payment():
    """Verify Razorpay payment for seva booking"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to continue'})
        
    try:
        data = request.get_json()
        
        # Get payment verification parameters
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        # Verify the payment signature
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Get booking ID from order notes
        order = razorpay_client.order.fetch(data.get('razorpay_order_id'))
        booking_id = order['notes'].get('booking_id')
        
        if not booking_id:
            return jsonify({'success': False, 'message': 'Booking ID not found in order'})
        
        # Update booking status
        booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'})
            
        # Update the existing booking status
        seva_collection.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "status": "confirmed",
                "payment_status": "completed",
                "transaction_id": data.get('razorpay_payment_id'),
                "payment_date": datetime.now()
            }}
        )
        
        # Find and remove any duplicate pending bookings for the same user, seva and date
        if booking:
            seva_collection.delete_many({
                "_id": {"$ne": ObjectId(booking_id)},
                "user_id": booking.get("user_id"),
                "seva_id": booking.get("seva_id"),
                "seva_date": booking.get("seva_date"),
                "status": "pending"
            })
        
        return jsonify({
            'success': True,
            'message': 'Payment verified and booking confirmed',
            'redirect_url': url_for('seva.payment_success', booking_id=booking_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@seva_bp.route('/process_payment/<booking_id>', methods=['GET', 'POST'])
def process_payment(booking_id):
    """Handle fake Razorpay payment processing"""
    if 'user' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('user.login'))
    
    try:
        # Fetch booking details
        booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Check if this booking belongs to the logged-in user
        if booking.get("user_id") != session["user"]["id"]:
            flash("Unauthorized access to booking.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Fetch seva details
        seva = seva_list.find_one({"_id": ObjectId(booking.get("seva_id"))})
        if not seva:
            flash("Seva details not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        if request.method == 'POST':
            # Generate a transaction ID
            transaction_id = f"rzp_{secrets.token_hex(6)}"
            payment_date = datetime.now()
            
            # Update booking status to completed
            seva_collection.update_one(
                {"_id": ObjectId(booking_id)},
                {"$set": {
                    "status": "confirmed",
                    "payment_status": "completed",
                    "transaction_id": transaction_id,
                    "payment_date": payment_date
                }}
            )
            
            # Find and remove any duplicate pending bookings for the same user, seva and date
            seva_collection.delete_many({
                "_id": {"$ne": ObjectId(booking_id)},
                "user_id": booking.get("user_id"),
                "seva_id": booking.get("seva_id"),
                "seva_date": booking.get("seva_date"),
                "status": "pending"
            })
            
            # Redirect to payment success page
            return redirect(url_for('seva.payment_success', booking_id=booking_id))
        
        # GET request - show payment page
        temple_name = "Shri Veeranjaneya Swamy Temple"
        return render_template(
            "user/fake_razorpay.html",
            seva=seva,
            booking_id=booking_id,
            temple_name=temple_name
        )
        
    except Exception as e:
        flash(f"An error occurred during payment: {str(e)}", "danger")
        return redirect(url_for('user.dashboard'))

@seva_bp.route('/payment_success/<booking_id>')
def payment_success(booking_id):
    """Display payment success page"""
    if 'user' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('user.login'))
    
    try:
        # Fetch booking details
        booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Check if this booking belongs to the logged-in user
        if booking.get("user_id") != session["user"]["id"]:
            flash("Unauthorized access to booking.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Fetch seva details
        seva = seva_list.find_one({"_id": ObjectId(booking.get("seva_id"))})
        if not seva:
            flash("Seva details not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Format payment date
        payment_date = booking.get("payment_date", datetime.now()).strftime("%d %b %Y, %I:%M %p")
        
        return render_template(
            "user/payment_success.html",
            seva=seva,
            transaction_id=booking.get("transaction_id", "N/A"),
            payment_date=payment_date
        )
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('user.dashboard'))

def generate_seva_receipt(booking_id):
    """Generate a PDF receipt for seva booking"""
    buffer = io.BytesIO()
    
    # Get booking details from database
    if isinstance(booking_id, str):
        booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
    else:
        booking = booking_id  # If booking data is directly provided
    
    # Get corresponding seva details
    seva = seva_list.find_one({"_id": ObjectId(booking["seva_id"])})
    if not seva:
        raise ValueError(f"Seva with ID {booking['seva_id']} not found")
        
    # Create a PDF document with ReportLab - Razorpay style
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add blue header bar like Razorpay
    p.setFillColorRGB(0, 112, 186)  # Razorpay blue
    p.rect(0, height-40, width, 40, fill=1)
    
    # Add payment receipt text in header
    p.setFillColorRGB(1, 1, 1)  # White text
    p.setFont("Helvetica-Bold", 18)
    p.drawString(30, height-25, "PAYMENT RECEIPT")
    
    # Add date on right side of header
    payment_date = booking.get("payment_date", datetime.now())
    if isinstance(payment_date, str):
        try:
            payment_date = datetime.strptime(payment_date, "%d %b %Y, %I:%M %p")
        except:
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()
    date_str = payment_date.strftime("%d %b %Y")
    p.setFont("Helvetica", 12)
    p.drawString(width-120, height-25, f"Date: {date_str}")
    
    # Reset color to black for main content
    p.setFillColorRGB(0, 0, 0)
    
    # Add temple logo area (placeholder text instead of logo)
    p.setStrokeColorRGB(0.9, 0.9, 0.9)
    p.setFillColorRGB(0.98, 0.98, 0.98)
    p.roundRect(30, height-130, 150, 70, 5, fill=1)
    
    # Add temple name in logo area
    p.setFont("Helvetica-Bold", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(105, height-90, "Shri Veeranjaneya Swamy Temple")
    p.setFont("Helvetica", 10)
    p.drawCentredString(105, height-105, "Charitable & Religious Trust")
    
    # Payment section heading
    p.setFont("Helvetica-Bold", 14)
    p.drawString(210, height-80, "PAYMENT DETAILS")
    p.line(210, height-85, 350, height-85)
    
    # Format amount with Indian number formatting
    try:
        amount = float(booking['seva_price'])
        amount_str = f"₹{amount:,.2f}"
    except:
        amount_str = f"₹{booking['seva_price']}"
    
    # Payment details
    p.setFont("Helvetica", 11)
    details_start_y = height-110
    line_height = 20
    
    # Create table-like structure for payment details
    payment_details = [
        ["Transaction ID:", booking.get("transaction_id", "N/A")],
        ["Amount Paid:", amount_str],
        ["Payment Status:", "Completed"],
        ["Payment Method:", "Razorpay"],
        ["Transaction Date:", payment_date.strftime("%d %b %Y, %I:%M %p")]
    ]
    
    for i, (label, value) in enumerate(payment_details):
        y_pos = details_start_y - (i * line_height)
        p.setFont("Helvetica", 11)
        p.drawString(210, y_pos, label)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(350, y_pos, value)
    
    # Seva details section
    seva_section_y = details_start_y - (len(payment_details) * line_height) - 30
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, seva_section_y, "SEVA DETAILS")
    p.line(30, seva_section_y - 5, 180, seva_section_y - 5)
    
    # Seva details content
    p.setFont("Helvetica", 11)
    seva_details = [
        ["Seva Name:", seva["seva_name"]],
        ["Seva Type:", seva["seva_type"]],
        ["Seva Date:", booking.get("seva_date", "Not specified")],
        ["Booking Date:", booking.get("booking_date", datetime.now()).strftime("%d %b %Y")],
        ["Booked By:", booking.get("user_name", "N/A")]
    ]
    
    for i, (label, value) in enumerate(seva_details):
        y_pos = seva_section_y - 25 - (i * line_height)
        p.setFont("Helvetica", 11)
        p.drawString(30, y_pos, label)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(120, y_pos, value)
    
    # Customer section
    customer_section_y = details_start_y - (len(payment_details) * line_height) - 30
    p.setFont("Helvetica-Bold", 14)
    p.drawString(210, customer_section_y, "CUSTOMER DETAILS")
    p.line(210, customer_section_y - 5, 360, customer_section_y - 5)
    
    # Customer details content
    p.setFont("Helvetica", 11)
    customer_details = [
        ["Name:", booking.get("user_name", "Not provided")],
        ["Email:", booking.get("email", "Not provided")],
        ["Phone:", booking.get("phone", "Not provided")]
    ]
    
    for i, (label, value) in enumerate(customer_details):
        y_pos = customer_section_y - 25 - (i * line_height)
        p.setFont("Helvetica", 11)
        p.drawString(210, y_pos, label)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(300, y_pos, value)
    
    # Add thank you message
    p.setFont("Helvetica", 12)
    p.drawString(30, 150, "Thank you for your booking and payment.")
    p.drawString(30, 130, "We look forward to performing the seva as per your request.")
    
    # Add footer with legal information
    p.setFont("Helvetica", 10)
    p.drawString(30, 100, "This receipt is an official record of your payment.")
    p.drawString(30, 85, "This is a computer-generated receipt and does not require a physical signature.")
    
    # Add blue footer bar
    p.setFillColorRGB(0, 112, 186)  # Razorpay blue
    p.rect(0, 0, width, 25, fill=1)
    
    # Add footer text
    p.setFillColorRGB(1, 1, 1)  # White text
    p.setFont("Helvetica", 8)
    footer_text = "This is a computer-generated receipt and does not require a physical signature."
    p.drawCentredString(width/2, 10, footer_text)
    
    # Add timestamp at bottom
    p.setFillColorRGB(0, 0, 0)  # Black text
    p.setFont("Helvetica", 8)
    p.drawString(30, 40, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save the PDF
    p.save()
    buffer.seek(0)
    return buffer

@seva_bp.route('/receipt/<booking_id>')
def get_seva_receipt(booking_id):
    """Generate and return a PDF receipt for a seva booking"""
    if 'user' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('user.login'))
    
    try:
        # Check if the ID is a payment ID (starting with 'pay_')
        if booking_id.startswith('pay_'):
            # If it's a payment ID, try to find the booking by transaction_id
            booking = seva_collection.find_one({"transaction_id": booking_id})
        else:
            # Try to find by ObjectId (handle potential format errors)
            try:
                booking = seva_collection.find_one({"_id": ObjectId(booking_id)})
            except:
                # If ObjectId conversion fails, try as-is (just in case)
                booking = seva_collection.find_one({"_id": booking_id})
                
        if not booking:
            # If still not found, try a broader search including transaction_id field
            booking = seva_collection.find_one({"transaction_id": booking_id})
            
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Check if this booking belongs to the logged-in user
        if booking.get("user_id") != session["user"]["id"] and not session.get('is_admin'):
            flash("Unauthorized access to booking.", "danger")
            return redirect(url_for('user.dashboard'))
        
        # Generate PDF receipt
        receipt_buffer = generate_seva_receipt(booking)
        
        # Create descriptive filename
        filename = f"seva_receipt_{booking_id}"
        if 'seva_name' in booking:
            # Remove any special characters from seva name
            safe_name = ''.join(c for c in booking['seva_name'] if c.isalnum() or c == '_' or c == '-')
            filename += f"_{safe_name}"
        
        # Determine if it should be displayed in the browser or downloaded
        as_attachment = request.args.get('download', 'true').lower() == 'true'
        
        return send_file(
            receipt_buffer,
            mimetype='application/pdf',
            as_attachment=as_attachment,
            download_name=f"{filename}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating receipt: {str(e)}", exc_info=True)
        flash(f"Error generating receipt: {str(e)}", "danger")
        return redirect(url_for('user.dashboard'))
