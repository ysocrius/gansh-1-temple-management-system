from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, current_app as app
from database import donations_list, donations_collection, user_collection
from bson.objectid import ObjectId
from datetime import datetime
import logging
import uuid
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from functools import wraps
import razorpay
import os
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Razorpay client
key_id = os.environ.get('key_id', 'rzp_test_6WWw11VMvM8MXw')
key_secret = os.environ.get('key_secret', '4akdtf9N66cjL36XOSNjXYBc')
razorpay_client = razorpay.Client(auth=(key_id, key_secret))

donations_bp = Blueprint("donations", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({
                'success': False,
                'message': 'Please log in to make a donation',
                'redirect': url_for('user.login')
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def generate_donation_receipt(donation_data):
    """Generate a PDF receipt for the donation"""
    buffer = io.BytesIO()
    
    # Get the most up-to-date donation data from database if only transaction_id is provided
    if isinstance(donation_data, str) or (isinstance(donation_data, dict) and len(donation_data.keys()) == 1 and 'transaction_id' in donation_data):
        transaction_id = donation_data if isinstance(donation_data, str) else donation_data['transaction_id']
        donation_data = donations_collection.find_one({"transaction_id": transaction_id})
        if not donation_data:
            raise ValueError(f"Donation with transaction ID {transaction_id} not found")
    
    # Create a PDF document with ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add receipt header with better styling
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Temple Donation Receipt")
    
    # Add horizontal line below title
    p.line(50, 740, 550, 740)
    
    # Add donation details with better formatting
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 710, "Transaction Details:")
    
    # Set font for values
    p.setFont("Helvetica", 12)
    
    # Get donation type name - first check if we already have it in the donation record
    donation_type_name = donation_data.get('donation_type_name', '')
    
    # If not found in record, try to look it up by ID
    if not donation_type_name:
        donation_type_id = donation_data['donation_type']
        donation_type_doc = donations_list.find_one({"donation_id": donation_type_id})
        if donation_type_doc and 'donation_name' in donation_type_doc:
            donation_type_name = donation_type_doc['donation_name']
        else:
            donation_type_name = donation_type_id
    
    # Format date properly
    donation_date = donation_data['date']
    if isinstance(donation_date, str):
        try:
            donation_date = datetime.strptime(donation_date, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                donation_date = datetime.fromisoformat(donation_date.replace('Z', '+00:00'))
            except:
                donation_date = datetime.now()  # Fallback
    
    date_str = donation_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format amount with Indian number formatting
    try:
        amount = float(donation_data['amount'])
        amount_str = f"₹{amount:,.2f}"
    except:
        amount_str = f"₹{donation_data['amount']}"
    
    # Add key details
    p.drawString(50, 680, f"Transaction ID: {donation_data['transaction_id']}")
    p.drawString(50, 660, f"Date: {date_str}")
    p.drawString(50, 640, f"Amount: {amount_str}")
    p.drawString(50, 620, f"Donation Type: {donation_type_name}")
    
    # Add donor information if not anonymous
    if not donation_data.get('is_anonymous'):
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 590, "Donor Information:")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 570, f"Name: {donation_data.get('donor_name', 'Not provided')}")
        p.drawString(50, 550, f"Email: {donation_data.get('email', 'Not provided')}")
        
        # Add phone if available
        if donation_data.get('phone'):
            p.drawString(50, 530, f"Phone: {donation_data['phone']}")
    
    # Add thank you message
    p.setFont("Helvetica", 12)
    y_position = 510 if not donation_data.get('is_anonymous') else 590
    p.drawString(50, y_position, "Thank you for your generous donation!")
    
    # Add footer with tax information
    p.setFont("Helvetica", 10)
    p.drawString(50, 100, "This receipt is valid for tax deduction under section 80G.")
    p.drawString(50, 85, "This is a computer-generated receipt and does not require a physical signature.")
    
    # Add timestamp
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save the PDF
    p.save()
    buffer.seek(0)
    return buffer

@donations_bp.route("/")
def index():
    """Display donation options page"""
    try:
        # Get donation types
        donation_types = list(donations_list.find())
        
        # Get recent donations - include all donations, will handle anonymity in template
        recent_donations = list(donations_collection.find({
            'status': 'completed'
        }).sort('date', -1).limit(10))
        
        # Add debugging log for recent donations
        for donation in recent_donations:
            logger.debug(f"Recent donation: ID={donation.get('transaction_id')}, is_anonymous={donation.get('is_anonymous')}, donor_name={donation.get('donor_name')}")
        
        return render_template(
            "user/donations.html",
            donation_types=donation_types,
            donation_goals=[],  # Empty list since donation goals feature is removed
            recent_donations=recent_donations
        )
    except Exception as e:
        app.logger.error(f"Error displaying donations page: {str(e)}")
        flash("Could not load donation options. Please try again later.", "danger")
        # Redirect to the home page from general blueprint
        return redirect(url_for('general.home'))

@donations_bp.route("/submit", methods=["POST"])
@login_required
def submit_donation():
    """Process a new donation with enhanced error handling and receipt generation"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Invalid request format'}), 400

        data = request.get_json()
        logger.debug("Received donation data: %s", data)

        # Validate required fields
        required_fields = ['donationId', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (TypeError, ValueError) as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        # Get payment ID if provided (for Razorpay payments)
        payment_id = data.get('paymentId', '')
        
        # If no payment ID, generate a unique transaction ID
        transaction_id = payment_id if payment_id else f"don_{uuid.uuid4().hex[:12]}"

        # Get donation type details
        donation_type_id = data['donationId']
        donation_type_name = donation_type_id  # Default to ID if not found
        
        # Try to get donation type name from database
        donation_type_doc = donations_list.find_one({"donation_id": donation_type_id})
        if donation_type_doc and 'donation_name' in donation_type_doc:
            donation_type_name = donation_type_doc['donation_name']

        # Create donation record
        user_data = session['user']
        donation = {
            'user_id': user_data['id'],
            'donation_type': donation_type_id,
            'donation_type_name': donation_type_name,
            'amount': amount,
            'is_recurring': data.get('isRecurring', False),
            'is_anonymous': data.get('isAnonymous', False),
            'date': datetime.now(),
            'transaction_id': transaction_id,
            'payment_id': payment_id,  # Store Razorpay payment ID separately
            'payment_method': data.get('paymentMethod', 'direct'),
            'status': 'completed',
            'donor_name': user_data.get('name', 'Anonymous'),
            'email': user_data.get('email', '')
        }

        # Add additional fields if provided
        for field in ['phone', 'notes', 'purpose']:
            if field in data:
                donation[field] = data[field]

        # Add goal information if it's a goal donation
        if 'goalTitle' in data:
            donation['goal_title'] = data['goalTitle']

        # Save to database
        result = donations_collection.insert_one(donation)
        if not result.acknowledged:
            raise Exception("Database insertion failed")

        # Generate receipt
        receipt_buffer = generate_donation_receipt(donation)

        return jsonify({
            'success': True,
            'message': 'Donation processed successfully',
            'data': {
                'transactionId': transaction_id,
                'date': donation['date'].strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'donationType': donation_type_name,
                'donationId': donation_type_id,
                'receipt_url': url_for('donations.get_receipt', transaction_id=transaction_id)
            }
        })

    except Exception as e:
        logger.error(f"Error processing donation: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@donations_bp.route("/receipt/<transaction_id>")
@login_required
def get_receipt(transaction_id):
    """Generate and return a PDF receipt for a donation"""
    try:
        # Log the transaction ID being requested
        logger.info(f"Receipt requested for transaction ID: {transaction_id}")
        
        # Try multiple methods to find the donation
        donation = None
        
        # First try by transaction ID
        donation = donations_collection.find_one({"transaction_id": transaction_id})
        
        # If not found, try by payment ID if it looks like a Razorpay ID
        if not donation and transaction_id.startswith('pay_'):
            donation = donations_collection.find_one({"payment_id": transaction_id})
        
        # If still not found, try by ObjectId if it's a valid ObjectId string
        if not donation and len(transaction_id) == 24:
            try:
                donation = donations_collection.find_one({"_id": ObjectId(transaction_id)})
            except:
                pass
                
        if not donation:
            logger.error(f"Donation not found for receipt: {transaction_id}")
            return jsonify({'success': False, 'message': 'Donation not found'}), 404

        # Log the donation data for debugging
        logger.debug(f"Found donation: {donation}")

        # Check if user has permission to view this receipt
        current_user_id = session['user']['id']
        donation_user_id = str(donation.get('user_id', ''))
        
        if donation_user_id != current_user_id and not donation.get('is_anonymous') and not session.get('is_admin'):
            logger.warning(f"Unauthorized receipt access: User {current_user_id} tried to access receipt for {donation_user_id}")
            return jsonify({'success': False, 'message': 'Unauthorized access to receipt'}), 403

        # Get donation type name for the filename
        donation_type = donation.get('donation_type', 'general')
        donation_type_doc = donations_list.find_one({"donation_id": donation_type})
        type_name = donation_type_doc.get('donation_name', donation_type) if donation_type_doc else donation_type
        
        # Use a more descriptive filename
        filename = f"donation_receipt_{transaction_id}"
        if 'amount' in donation:
            try:
                amount = float(donation['amount'])
                filename += f"_{int(amount)}"
            except:
                pass
                
        # Generate the PDF receipt
        receipt_buffer = generate_donation_receipt(donation)
        
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
        return jsonify({'success': False, 'message': f'Error generating receipt: {str(e)}'}), 500

@donations_bp.route("/public-receipt/<transaction_id>")
def get_receipt_public(transaction_id):
    """Generate and return a PDF receipt for a donation without requiring login"""
    try:
        # Log the transaction ID being requested
        logger.info(f"Public receipt requested for transaction ID: {transaction_id}")
        
        # Try multiple methods to find the donation
        donation = None
        
        # First try by transaction ID
        donation = donations_collection.find_one({"transaction_id": transaction_id})
        
        # If not found, try by payment ID if it looks like a Razorpay ID
        if not donation and transaction_id.startswith('pay_'):
            donation = donations_collection.find_one({"payment_id": transaction_id})
        
        # If still not found, try by ObjectId if it's a valid ObjectId string
        if not donation and len(transaction_id) == 24:
            try:
                donation = donations_collection.find_one({"_id": ObjectId(transaction_id)})
            except:
                pass
                
        if not donation:
            logger.error(f"Donation not found for public receipt: {transaction_id}")
            return jsonify({'success': False, 'message': 'Donation not found'}), 404

        # Log the donation data for debugging
        logger.debug(f"Found donation for public receipt: {donation}")

        # Get donation type name for the filename
        donation_type = donation.get('donation_type', 'general')
        donation_type_doc = donations_list.find_one({"donation_id": donation_type})
        type_name = donation_type_doc.get('donation_name', donation_type) if donation_type_doc else donation_type
        
        # Use a more descriptive filename
        filename = f"donation_receipt_{transaction_id}"
        if 'amount' in donation:
            try:
                amount = float(donation['amount'])
                filename += f"_{int(amount)}"
            except:
                pass
                
        # Generate the PDF receipt
        receipt_buffer = generate_donation_receipt(donation)
        
        # Determine if it should be displayed in the browser or downloaded
        as_attachment = request.args.get('download', 'true').lower() == 'true'
        
        return send_file(
            receipt_buffer,
            mimetype='application/pdf',
            as_attachment=as_attachment,
            download_name=f"{filename}.pdf"
        )

    except Exception as e:
        logger.error(f"Error generating public receipt: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error generating receipt: {str(e)}'}), 500

@donations_bp.route("/goals")
def get_donation_goals():
    """Get updated donation goals with real-time progress"""
    try:
        # Return empty list as donation goals feature is removed
        return jsonify({
            'success': True,
            'data': []
        })
    except Exception as e:
        logger.error(f"Error fetching donation goals: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Error fetching donation goals'}), 500

# Add endpoint to view donation details
@donations_bp.route("/donation-details/<donation_id>")
def donation_details(donation_id):
    """Get details of a specific donation"""
    
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required",
            "redirect": url_for("user.login")
        }), 401
    
    try:
        # Ensure valid ObjectId
        try:
            if len(donation_id) == 24:  # Likely an ObjectId
                donation = donations_collection.find_one({"_id": ObjectId(donation_id)})
            else:
                donation = donations_collection.find_one({"transaction_id": donation_id})
                
        except:
            # If not a valid ObjectId, try as a transaction ID
            donation = donations_collection.find_one({"transaction_id": donation_id})
        
        if not donation:
            return jsonify({
                "status": "error",
                "message": f"Donation not found: {donation_id}"
            }), 404
        
        # Convert ObjectId to string
        if "_id" in donation:
            donation["id"] = str(donation["_id"])
            del donation["_id"]
        
        # Convert date to string format
        if "date" in donation and isinstance(donation["date"], datetime):
            donation["date"] = donation["date"].strftime("%Y-%m-%d %H:%M:%S")
        
        # Return donation details
        return jsonify({
            "status": "success",
            "donation": donation
        })
        
    except Exception as e:
        logger.error(f"Error fetching donation details: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Could not fetch donation details",
            "error": str(e)
        }), 500

@donations_bp.route("/create-payment", methods=["POST"])
@login_required
def create_payment():
    """Create a Razorpay order for donation payment"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Invalid request format'}), 400
            
        data = request.get_json()
        logger.debug("Received payment data: %s", data)
        
        # Validate amount
        try:
            amount = float(data.get('amount', 0))
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (TypeError, ValueError) as e:
            return jsonify({'success': False, 'message': str(e)}), 400
            
        # Convert amount to paise (Razorpay expects amount in smallest currency unit)
        amount_in_paise = int(amount * 100)
        
        # Create Razorpay order
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'don_{uuid.uuid4().hex[:8]}',
            'notes': {
                'donation_type': data.get('donationId', 'general'),
                'user_id': session.get('user', {}).get('id', 'anonymous')
            }
        }
        
        # Create the order
        order = razorpay_client.order.create(order_data)
        logger.debug("Razorpay order created: %s", order)
        
        # Return the order details to the client
        return jsonify({
            'success': True,
            'data': {
                'order_id': order['id'],
                'amount': amount,
                'currency': 'INR',
                'key_id': key_id
            }
        })
    
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@donations_bp.route("/verify-payment", methods=["POST"])
def verify_payment():
    try:
        data = request.get_json()
        logger.debug("Received payment verification data: %s", data)
        print("Verify payment request received:", data)
        
        # Log the isAnonymous flag specifically
        is_anonymous = data.get('isAnonymous', False)
        logger.debug("Donation anonymity flag: %s (type: %s)", is_anonymous, type(is_anonymous))
        print("Donation anonymity flag:", is_anonymous, "type:", type(is_anonymous))
        
        # Check if required parameters are present
        required_params = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for param in required_params:
            if not data or not data.get(param):
                logger.error(f"Missing required parameter: {param}")
                print(f"Missing required parameter: {param}")
                return jsonify({
                    'success': False, 
                    'message': f'Missing required parameter: {param}'
                }), 400
        
        # Get payment verification parameters
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        try:
            # Verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)
        except Exception as signature_error:
            logger.error(f"Signature verification failed: {str(signature_error)}")
            print(f"Signature verification failed: {str(signature_error)}")
            return jsonify({
                'success': False, 
                'message': 'Payment signature verification failed. Please contact support if payment was deducted.'
            }), 400
        
        # Get the order details
        try:
            order = razorpay_client.order.fetch(data.get('razorpay_order_id'))
        except Exception as order_error:
            logger.error(f"Could not fetch order details: {str(order_error)}")
            print(f"Could not fetch order details: {str(order_error)}")
            return jsonify({
                'success': False, 
                'message': 'Could not fetch order details. Please check payment status in your account.'
            }), 400
        
        # Check for user session, but don't require it
        user_data = None
        user_id = None
        if 'user' in session:
            user_data = session['user']
            user_id = user_data.get('id')
        else:
            # Try to get user ID from order notes as fallback
            user_id = order['notes'].get('user_id')
            # Try to get user data from database using the ID
            if user_id and user_id != 'anonymous':
                user_doc = user_collection.find_one({"_id": ObjectId(user_id)})
                if user_doc:
                    user_data = {
                        'id': str(user_doc['_id']),
                        'name': user_doc.get('name', 'Anonymous'),
                        'email': user_doc.get('email', ''),
                        'phone': user_doc.get('phone', '')
                    }
        
        donation_type_id = order['notes'].get('donation_type', 'general')
        amount = float(order['amount']) / 100  # Convert paise to rupees
        
        # Get donation type details
        donation_type_name = donation_type_id  # Default to ID if not found
        
        # Try to get donation type name from database
        donation_type_doc = donations_list.find_one({"donation_id": donation_type_id})
        if donation_type_doc and 'donation_name' in donation_type_doc:
            donation_type_name = donation_type_doc['donation_name']
        
        # Get payment details for additional information
        payment_id = data.get('razorpay_payment_id')
        payment_info = {}
        
        try:
            if payment_id:
                payment_info = razorpay_client.payment.fetch(payment_id)
                logger.debug(f"Payment details fetched: {payment_info}")
        except Exception as e:
            logger.warning(f"Could not fetch payment details: {str(e)}")
            print(f"Could not fetch payment details: {str(e)}")
        
        # Default donor information if user is not authenticated
        donor_name = 'Anonymous'
        donor_email = ''
        donor_phone = ''
        
        # Use user data if available
        if user_data:
            donor_name = user_data.get('name', 'Anonymous')
            donor_email = user_data.get('email', '')
            donor_phone = user_data.get('phone', '')
        
        # Create donation document with consistent transaction ID
        donation = {
            'user_id': user_id if user_id else 'anonymous',
            'donation_type': donation_type_id,
            'donation_type_name': donation_type_name,
            'amount': amount,
            'is_recurring': bool(data.get('isRecurring', False)),
            'is_anonymous': bool(data.get('isAnonymous', False)),
            'date': datetime.now(),
            'transaction_id': payment_id,  # Use Razorpay payment ID as transaction ID
            'payment_id': payment_id,      # Store payment ID separately too
            'order_id': data.get('razorpay_order_id'),
            'status': 'completed',
            'donor_name': donor_name,
            'email': donor_email,
            'phone': donor_phone
        }
        
        # Log the donation data for debugging
        logger.debug(f"Creating donation with data: {donation}")
        print(f"Creating donation with anonymous flag: {donation['is_anonymous']}")
        
        # Add additional payment details if available
        if payment_info:
            if 'card' in payment_info:
                donation['payment_method'] = f"Card ({payment_info['card'].get('last4', '****')})"
            elif 'method' in payment_info:
                donation['payment_method'] = payment_info['method']
            elif 'upi' in payment_info:
                donation['payment_method'] = f"UPI ({payment_info['upi'].get('vpa', '')})"
            elif 'wallet' in payment_info and payment_info['wallet']:
                donation['payment_method'] = f"Wallet ({payment_info['wallet']})"
                
            if 'bank' in payment_info:
                donation['bank'] = payment_info['bank']
                
        # Save to database
        try:
            result = donations_collection.insert_one(donation)
            if not result.acknowledged:
                raise Exception("Database insertion failed")
            print(f"Donation record created for payment ID: {payment_id}")
        except Exception as db_error:
            logger.error(f"Database error saving donation: {str(db_error)}")
            print(f"Database error saving donation: {str(db_error)}")
            # Still return success since payment was successful
            # We'll log the error but not fail the transaction from user perspective
        
        # Create a direct receipt URL that doesn't require login
        receipt_url = url_for('donations.get_receipt_public', transaction_id=payment_id)
        
        return jsonify({
            'success': True,
            'message': 'Payment verified and donation recorded',
            'data': {
                'transactionId': payment_id,
                'date': donation['date'].strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'donationType': donation_type_name,
                'donationId': donation_type_id,
                'receipt_url': receipt_url,
                'razorpay_payment_id': payment_id,
                'payment_id': payment_id,  # Add this for compatibility with new client code
                'redirect_url': url_for('donations.public_payment_success', transaction_id=payment_id)  # Direct to public success page
            }
        })
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        print(f"Error verifying payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An error occurred while verifying your payment. If payment was deducted, please contact support.',
            'error': str(e)
        }), 500

@donations_bp.route("/test-receipt/<donation_type>/<amount>")
@login_required
def test_receipt(donation_type, amount):
    """Generate a test receipt with the specified details"""
    try:
        # Only allow in development mode
        if app.config.get('ENV') != 'development' and not app.debug:
            return jsonify({'success': False, 'message': 'Test receipts only available in development mode'}), 403
            
        # Create a test donation
        user_data = session['user']
        test_amount = float(amount)
        test_transaction_id = f"test_pay_{uuid.uuid4().hex[:8]}"
        
        donation = {
            'user_id': user_data['id'],
            'donation_type': donation_type,
            'amount': test_amount,
            'is_anonymous': False,
            'date': datetime.now(),
            'transaction_id': test_transaction_id,
            'payment_id': test_transaction_id,
            'status': 'test',
            'donor_name': user_data.get('name', 'Test Donor'),
            'email': user_data.get('email', 'test@example.com'),
            'phone': user_data.get('phone', '9999999999')
        }
        
        # Save to database with test flag
        donation['is_test'] = True
        result = donations_collection.insert_one(donation)
        
        if not result.acknowledged:
            raise Exception("Could not save test donation")
            
        # Redirect to receipt page
        return redirect(url_for('donations.get_receipt', transaction_id=test_transaction_id))
        
    except Exception as e:
        logger.error(f"Error creating test receipt: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@donations_bp.route("/payment_success/<transaction_id>")
@login_required
def payment_success(transaction_id):
    """Display payment success page for donation"""
    try:
        # Try multiple methods to find the donation
        donation = None
        
        # First try by transaction ID
        donation = donations_collection.find_one({"transaction_id": transaction_id})
        
        # If not found, try by payment ID if it looks like a Razorpay ID
        if not donation and transaction_id.startswith('pay_'):
            donation = donations_collection.find_one({"payment_id": transaction_id})
        
        # If still not found, try by ObjectId if it's a valid ObjectId string
        if not donation and len(transaction_id) == 24:
            try:
                donation = donations_collection.find_one({"_id": ObjectId(transaction_id)})
            except:
                pass
                
        if not donation:
            flash("Donation not found.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Check if this donation belongs to the logged-in user
        if str(donation.get("user_id")) != session["user"]["id"]:
            flash("Unauthorized access to donation.", "danger")
            return redirect(url_for('user.dashboard'))
            
        # Format payment date
        payment_date = donation.get("date", datetime.now()).strftime("%d %b %Y, %I:%M %p")
        
        # Get donation type details
        donation_type = donation.get('donation_type', 'general')
        donation_type_name = donation.get('donation_type_name', '')
        
        if not donation_type_name:
            # Try to get donation type name from database
            donation_type_doc = donations_list.find_one({"donation_id": donation_type})
            if donation_type_doc and 'donation_name' in donation_type_doc:
                donation_type_name = donation_type_doc['donation_name']
            else:
                donation_type_name = donation_type
                
        # Format the amount
        amount = donation.get('amount', 0)
        
        return render_template(
            "user/donation_payment_success.html",
            donation_type=donation_type_name,
            transaction_id=donation.get("transaction_id", "N/A"),
            payment_id=donation.get("payment_id", "N/A"),
            amount=amount,
            payment_date=payment_date
        )
        
    except Exception as e:
        app.logger.error(f"Error displaying donation success page: {str(e)}")
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('user.dashboard'))

@donations_bp.route("/public-payment-success/<transaction_id>")
def public_payment_success(transaction_id):
    """Display payment success page for donation without requiring login"""
    try:
        # Try multiple methods to find the donation
        donation = None
        
        # First try by transaction ID
        donation = donations_collection.find_one({"transaction_id": transaction_id})
        
        # If not found, try by payment ID if it looks like a Razorpay ID
        if not donation and transaction_id.startswith('pay_'):
            donation = donations_collection.find_one({"payment_id": transaction_id})
        
        # If still not found, try by ObjectId if it's a valid ObjectId string
        if not donation and len(transaction_id) == 24:
            try:
                donation = donations_collection.find_one({"_id": ObjectId(transaction_id)})
            except:
                pass
                
        if not donation:
            return render_template(
                "user/donation_payment_success.html",
                transaction_id="Not Found",
                payment_id="Not Found",
                amount=0,
                payment_date=datetime.now().strftime("%d %b %Y, %I:%M %p"),
                donation_type="Unknown",
                is_public=True,
                error=True,
                error_message="Donation record not found. If you have made a payment, please contact support with your payment details."
            )
            
        # Format payment date
        payment_date = donation.get("date", datetime.now()).strftime("%d %b %Y, %I:%M %p")
        
        # Get donation type details
        donation_type = donation.get('donation_type', 'general')
        donation_type_name = donation.get('donation_type_name', '')
        
        if not donation_type_name:
            # Try to get donation type name from database
            donation_type_doc = donations_list.find_one({"donation_id": donation_type})
            if donation_type_doc and 'donation_name' in donation_type_doc:
                donation_type_name = donation_type_doc['donation_name']
            else:
                donation_type_name = donation_type
                
        # Format the amount
        amount = donation.get('amount', 0)
        
        return render_template(
            "user/donation_payment_success.html",
            donation_type=donation_type_name,
            transaction_id=donation.get("transaction_id", "N/A"),
            payment_id=donation.get("payment_id", "N/A"),
            amount=amount,
            payment_date=payment_date,
            is_public=True,
            receipt_url=url_for('donations.get_receipt_public', transaction_id=transaction_id)
        )
        
    except Exception as e:
        app.logger.error(f"Error displaying donation success page: {str(e)}")
        return render_template(
            "user/donation_payment_success.html", 
            error=True,
            error_message=f"An error occurred: {str(e)}",
            is_public=True
        )