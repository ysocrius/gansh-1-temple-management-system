from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app as app, jsonify, g
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import bcrypt
import secrets
from werkzeug.security import generate_password_hash
from database import user_collection, donations_collection, seva_collection, donation_goals_collection, events_collection
from bson import ObjectId
from datetime import datetime
import random  
from functools import wraps
from pymongo.errors import PyMongoError
import logging
from utils.mail import mail
import time
import os
from authlib.integrations.flask_client import OAuth
import requests

# Get the Flask app logger
logger = logging.getLogger('app')

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Initialize OAuth
oauth = OAuth()

# Configure OAuth at blueprint setup time, not at import time
@user_bp.record_once
def setup_oauth(state):
    app = state.app
    oauth.init_app(app)
    # Register the Google OAuth client
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID', ''),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET', ''),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email profile'},
    )

# Use a function to create the serializer with the app's secret key
def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app.logger.debug(f"Checking login requirement. Session: {session}")
        
        if 'user' not in session:
            app.logger.warning("User not in session - redirecting to login")
            flash('Please log in to access this page.', 'warning')
            response = redirect(url_for('user.login'))
            
            # Add cache control headers
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            return response
            
        # If here, user is in session - ensure it's properly validated
        user_id = session['user'].get('id')
        if not user_id:
            app.logger.warning("Invalid user data in session")
            session.clear()
            flash('Invalid session. Please log in again.', 'warning')
            return redirect(url_for('user.login'))
            
        # Mark session as modified to extend its lifetime
        session.modified = True
        
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------
#  USER REGISTRATION (Email Verification)
# ----------------------------------

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form.get("password")

        # Check if email or phone already exists
        if user_collection.find_one({"email": email}):
            flash("Email is already registered!", "danger")
            return redirect(url_for("user.register"))
        if user_collection.find_one({"phone": phone}):
            flash("Phone number is already registered!", "danger")
            return redirect(url_for("user.register"))

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Generate 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=6))
        
        # Set OTP expiration time (10 minutes from now)
        expiration_time = time.time() + 600  # 10 minutes in seconds

        # Save user as unverified in DB
        user_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": hashed_password,
            "verified": False,
            "registration_otp": otp,
            "registration_otp_time": expiration_time,
            "created_at": datetime.now()
        }
        user_collection.insert_one(user_data)

        # Log email configuration before sending
        app.logger.debug(f"Mail config - SERVER: {app.config.get('MAIL_SERVER')}, PORT: {app.config.get('MAIL_PORT')}")
        app.logger.debug(f"Mail config - USERNAME: {app.config.get('MAIL_USERNAME')}, SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        app.logger.debug(f"OTP generated: {otp} for email: {email}")

        # Store email in session to maintain context
        session['email'] = email
        session.modified = True

        # Send OTP email
        try:
            send_registration_otp(email, otp)
            flash("Registration successful! Please verify your email with the OTP we sent.", "success")
        except Exception as e:
            app.logger.error(f"Failed to send registration OTP: {str(e)}")
            flash(f"Registration successful but couldn't send verification OTP. Please try again or contact support. Error: {str(e)}", "warning")
        
        return redirect(url_for("user.verify_registration_otp", email=email))

    return render_template("user/register.html")


def send_registration_otp(email, otp):
    """Send registration verification OTP email and return True if successful, False otherwise"""
    subject = "Your Email Verification OTP"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #FF7F00;">Email Verification OTP</h2>
        <p>Thank you for registering. Please use the following OTP to verify your email address:</p>
        <div style="background-color: #f7f7f7; padding: 15px; font-size: 24px; text-align: center; letter-spacing: 5px; font-weight: bold; margin: 20px 0;">
            {otp}
        </div>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you did not sign up for an account, please ignore this email.</p>
        <p>Thank you,<br>Temple Management Team</p>
    </div>
    """

    msg = Message(subject, sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[email])
    msg.html = html_content
    msg.body = f"Your OTP for email verification is: {otp}. It expires in 10 minutes."

    try:
        # Log mail settings before sending
        app.logger.debug(f"Sending mail with: SERVER={app.config.get('MAIL_SERVER')}, PORT={app.config.get('MAIL_PORT')}")
        app.logger.debug(f"Using credentials: USERNAME={app.config.get('MAIL_USERNAME')}, SENDER={app.config.get('MAIL_DEFAULT_SENDER')}")
        
        mail.send(msg)
        app.logger.info(f"Registration OTP email sent successfully to {email}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending registration OTP email to {email}: {str(e)}")
        print(f"Error sending registration OTP email: {e}")
        return False


# ----------------------------------
#  VERIFY REGISTRATION OTP
# ----------------------------------

@user_bp.route("/verify-registration-otp", methods=["GET", "POST"])
def verify_registration_otp():
    """Handle OTP verification for newly registered users"""
    # Add detailed debug logging
    app.logger.debug(f"verify_registration_otp route called. Method: {request.method}")
    app.logger.debug(f"Session state: {dict(session)}")
    app.logger.debug(f"Request args: {dict(request.args)}")
    
    # Get email from request args or session
    email = request.args.get('email') or session.get('email')
    
    if not email:
        app.logger.warning("No email in session or parameters, redirecting to register")
        flash('Session expired. Please register again.', 'danger')
        return redirect(url_for('user.register'))
    
    # Store email in session as backup
    session['email'] = email
    session.modified = True
    
    # Get user from database
    user = user_collection.find_one({"email": email})
    if not user:
        app.logger.warning(f"User not found for email: {email}")
        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('user.register'))
    
    # If user is already verified, redirect to login
    if user.get('verified', False):
        flash('Your account is already verified. Please log in.', 'info')
        return redirect(url_for('user.login'))
    
    # Check if OTP exists and has not expired
    current_time = time.time()
    if 'registration_otp_time' not in user or current_time > user['registration_otp_time']:
        app.logger.warning(f"OTP expired or not found for email: {email}")
        
        # Generate new OTP
        otp = ''.join(random.choices('0123456789', k=6))
        expiration_time = time.time() + 600  # 10 minutes in seconds
        
        # Update OTP in database
        user_collection.update_one(
            {"email": email},
            {"$set": {
                "registration_otp": otp,
                "registration_otp_time": expiration_time
            }}
        )
        
        # Resend OTP
        try:
            send_registration_otp(email, otp)
            flash('Previous OTP has expired. A new OTP has been sent to your email.', 'info')
        except Exception as e:
            app.logger.error(f"Failed to send new OTP: {str(e)}")
            flash('Failed to send a new OTP. Please try again.', 'danger')
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = user.get('registration_otp')
        
        app.logger.debug(f"OTP entered: {entered_otp}")
        app.logger.debug(f"Stored OTP in MongoDB: {stored_otp}")
        
        # Validate OTP format first
        if not entered_otp or not entered_otp.isdigit() or len(entered_otp) != 6:
            flash('OTP must be a 6-digit number. Please check and try again.', 'warning')
            return render_template('user/verify_registration_otp.html', email=email)
        
        # Get failed attempts counter or initialize to zero
        failed_attempts = user.get('otp_failed_attempts', 0)
        
        # Check if OTP is correct
        if stored_otp and entered_otp == stored_otp:
            app.logger.debug("OTP verification successful")
            
            # Mark user as verified in MongoDB
            user_collection.update_one(
                {"email": email},
                {"$set": {"verified": True}, 
                 "$unset": {"registration_otp": "", "registration_otp_time": "", "otp_failed_attempts": ""}}
            )
            
            # Set success flash message right here
            flash('Email verified successfully! You can now log in with your credentials.', 'success')
            
            # Clear just the email from session but keep flash messages
            session.pop('email', None)
            
            # Redirect to login with success parameter for double surety
            return redirect(url_for('user.login', verified='success'))
        
        # OTP is incorrect
        app.logger.warning("Invalid OTP entered")
        
        # Increment failed attempts counter (max 5 attempts)
        failed_attempts += 1
        
        # Update failed attempts in database
        user_collection.update_one(
            {"email": email},
            {"$set": {"otp_failed_attempts": failed_attempts}}
        )
        
        # Different messages based on number of failed attempts
        if failed_attempts >= 5:
            # Generate new OTP after 5 failed attempts
            otp = ''.join(random.choices('0123456789', k=6))
            expiration_time = time.time() + 600  # 10 minutes in seconds
            
            # Update OTP in database
            user_collection.update_one(
                {"email": email},
                {"$set": {
                    "registration_otp": otp,
                    "registration_otp_time": expiration_time,
                    "otp_failed_attempts": 0
                }}
            )
            
            # Send new OTP
            try:
                send_registration_otp(email, otp)
                flash('Too many failed attempts. A new OTP has been sent to your email.', 'warning')
            except Exception as e:
                app.logger.error(f"Failed to send new OTP after failed attempts: {str(e)}")
                flash('Failed to send a new OTP. Please try again later.', 'danger')
        else:
            remaining_attempts = 5 - failed_attempts
            flash(f'Invalid OTP. Please try again. {remaining_attempts} attempts remaining.', 'danger')
    
    return render_template('user/verify_registration_otp.html', email=email)


@user_bp.route("/verify/<token>")
def verify_email(token):
    try:
        app.logger.debug(f"Verify email called with token: {token}")
        serializer = get_serializer()
        email = serializer.loads(token, salt="email-confirm", max_age=86400)  # Extend token validity to 24 hours
        
        app.logger.debug(f"Email extracted from token: {email}")
        user = user_collection.find_one({"email": email})
        
        if user:
            app.logger.debug(f"User found: {user.get('name')}, current verification status: {user.get('verified', False)}")
            # Update user document to mark as verified
            result = user_collection.update_one(
                {"email": email},
                {"$set": {"verified": True}, "$unset": {"token": ""}}
            )
            
            app.logger.debug(f"MongoDB update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.modified_count > 0:
                flash("Email verified successfully! You can now log in. Note: We've moved to OTP-based verification for new registrations.", "success")
            else:
                app.logger.warning(f"User document was not modified during verification. Already verified: {user.get('verified', False)}")
                flash("Email verification already completed. You can now log in.", "info")
            
            # Double-check verification status
            updated_user = user_collection.find_one({"email": email})
            app.logger.debug(f"After update verification status: {updated_user.get('verified', False)}")
            
            return redirect(url_for("user.login"))
        else:
            app.logger.warning(f"User not found for email: {email} during verification")
            flash("Invalid verification link. User not found.", "danger")

    except Exception as e:
        app.logger.error(f"Error verifying email with token: {str(e)}", exc_info=True)
        flash("Invalid or expired verification link! We've moved to OTP-based verification. Please register again or request a verification OTP.", "danger")

    return redirect(url_for("user.login"))


def send_verification_email(email, token):
    try:
        verify_url = url_for("user.verify_email", token=token, _external=True)
        app.logger.debug(f"Generated verification URL: {verify_url}")
        
        subject = "Verify Your Email"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: #FF7F00;">Email Verification</h2>
            <p>Thank you for registering. Please click the link below to verify your email address:</p>
            <p><a href="{verify_url}" style="background-color: #FF7F00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
            <p>If the button doesn't work, please copy and paste this URL into your browser:</p>
            <p>{verify_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not sign up for this account, please ignore this email.</p>
        </div>
        """

        msg = Message(subject, sender=app.config.get("MAIL_DEFAULT_SENDER"), recipients=[email])
        msg.html = html_content
        msg.body = f"Please verify your email by visiting this link: {verify_url}"

        # Log mail settings before sending
        app.logger.debug(f"Sending mail with: SERVER={app.config.get('MAIL_SERVER')}, PORT={app.config.get('MAIL_PORT')}")
        app.logger.debug(f"Using credentials: USERNAME={app.config.get('MAIL_USERNAME')}, SENDER={app.config.get('MAIL_DEFAULT_SENDER')}")
        
        mail.send(msg)
        app.logger.info(f"Verification email sent successfully to {email}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending verification email to {email}: {str(e)}", exc_info=True)
        print(f"Error sending verification email: {e}")
        return False


# ----------------------------------
#  GOOGLE OAUTH LOGIN
# ----------------------------------

@user_bp.route('/google_login')
def google_login():
    """Initiate the Google OAuth login flow"""
    app.logger.info("Initiating Google login flow")
    # Use the current_app to get oauth client
    redirect_uri = url_for('user.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@user_bp.route('/google_callback')
def google_callback():
    """Handle the Google OAuth callback"""
    try:
        # Get the token from the callback
        token = oauth.google.authorize_access_token()
        if not token:
            flash("Authentication failed. Please try again.", "danger")
            return redirect(url_for('user.login'))
            
        # Get user info from Google
        resp = oauth.google.get('userinfo')
        user_info = resp.json()
        
        app.logger.info(f"Google callback received for user: {user_info.get('email')}")
        
        # Check if user exists in our database
        email = user_info.get('email')
        user = user_collection.find_one({"email": email})
        
        if user:
            # User exists, log them in
            app.logger.info(f"Existing user found with Google login: {email}")
            
            # Check if user is already verified through regular signup
            if not user.get('verified', False):
                # Auto-verify the user since they verified through Google
                user_collection.update_one(
                    {"email": email},
                    {"$set": {"verified": True}}
                )
            
            # Store user data in session
            session.permanent = True
            
            session['user'] = {
                'id': str(user['_id']),
                'name': user.get('name', user_info.get('name', 'User')),
                'email': email,
                'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'login_method': 'google'
            }
            
            session.modified = True
            
            flash("Login successful with Google!", "success")
            return redirect(url_for("user.dashboard"))
        else:
            # User doesn't exist, create a new user
            app.logger.info(f"Creating new user from Google login: {email}")
            
            # Generate a random secure password for the user
            random_password = secrets.token_hex(16)
            hashed_password = bcrypt.hashpw(random_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            # Create user document
            user_data = {
                "name": user_info.get('name', 'Google User'),
                "email": email,
                "password": hashed_password,
                "verified": True,  # Auto-verified since they verified with Google
                "created_at": datetime.now(),
                "google_id": user_info.get('id'),
                "picture": user_info.get('picture')
            }
            
            # Add phone field with placeholder if required
            if 'phone' in user_collection.find_one({}, {'phone': 1}):
                user_data["phone"] = ""  # Empty placeholder
            
            result = user_collection.insert_one(user_data)
            
            # Store user in session
            session.permanent = True
            
            session['user'] = {
                'id': str(result.inserted_id),
                'name': user_info.get('name', 'Google User'),
                'email': email,
                'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'login_method': 'google'
            }
            
            session.modified = True
            
            flash("Account created and logged in with Google!", "success")
            return redirect(url_for("user.dashboard"))
            
    except Exception as e:
        app.logger.error(f"Error in Google callback: {str(e)}", exc_info=True)
        flash("Authentication error. Please try again.", "danger")
        return redirect(url_for("user.login"))

# ----------------------------------
#  LOGIN
# ----------------------------------

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    # Check for parameter flags in URL
    reset_success = request.args.get('reset') == 'success'
    register_success = request.args.get('register') == 'success'
    verified_success = request.args.get('verified') == 'success'
    
    # Remember the next parameter if it's provided in the URL
    next_url = request.args.get('next')
    
    # Set flash messages based on URL parameters *before* clearing session
    if reset_success:
        flash('Password has been reset successfully. Please login.', 'success')
    if register_success:
        flash('Registration successful! Please check your email for the verification OTP.', 'success')
    if verified_success and 'user' not in session:  # Only set this if no flash message present
        flash('Email verified successfully! You can now log in with your credentials.', 'success')
    
    # Only clear session if not coming from verification (to preserve flash messages)
    if not verified_success:
        session.clear()
    else:
        # Just clear user data but preserve flash messages
        session.pop('email', None)
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        app.logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return redirect(url_for("user.login"))
        
        # Fetch user from MongoDB
        user = user_collection.find_one({"email": email})
        app.logger.info(f"User found: {bool(user)}")
        
        if user:
            app.logger.debug(f"User verification status: {user.get('verified', False)}, User ID: {user.get('_id')}")
            verification_status = user.get("verified", False)
            
            if verification_status:
                stored_password = user.get("password", "")
                
                if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                    # Store user data in session
                    session.permanent = True  # Make the session persistent
                    
                    # Add user data to session
                    session['user'] = {
                        'id': str(user['_id']),
                        'name': user.get('name', 'User'),
                        'email': user['email'],
                        'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Force the session to be saved
                    session.modified = True
                    
                    app.logger.info(f"Login successful for user: {email}")
                    app.logger.debug(f"Session after login: {session}")
                    app.logger.debug(f"Session contains user: {'user' in session}")
                    
                    # Check session configuration
                    app.logger.debug(f"Session permanent: {session.permanent}")
                    app.logger.debug(f"Session sid: {session.sid if hasattr(session, 'sid') else 'Not available'}")
                    
                    flash("Login successful!", "success")
                    
                    # Redirect to the next URL if provided, otherwise to dashboard
                    if next_url:
                        return redirect(next_url)
                    else:
                        return redirect(url_for("user.dashboard"))
                else:
                    app.logger.warning(f"Invalid password for user: {email}")
                    flash("Invalid email or password!", "danger")
            else:
                app.logger.warning(f"Unverified user attempting to log in: {email}")
                flash("Please verify your email before logging in.", "warning")
                
                # Show resend verification link
                return render_template("user/login.html", show_resend=True, email=email, next=next_url)
        else:
            app.logger.warning(f"User not found for email: {email}")
            flash("Invalid email or password!", "danger")
    
    return render_template("user/login.html", next=next_url)


@user_bp.route("/logout")
def logout():
    if 'user' in session:
        app.logger.info(f"User logged out: {session['user'].get('email')}")
    session.clear()
    flash("Logged out successfully!", "info")
    response = redirect(url_for("user.login"))
    
    # Add cache control headers to prevent caching protected pages
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response


@user_bp.route("/dashboard")
@login_required
def dashboard():
    app.logger.debug(f"Session content in dashboard route: {session}")
    app.logger.debug(f"Session contains user: {'user' in session}")
    
    user_data = session.get('user', {})
    if not user_data:
        app.logger.warning("User data not found in session despite @login_required")
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('user.login'))
    
    try:
        # Get user's statistics
        user_id = user_data.get('id')
        app.logger.debug(f"User ID from session: {user_id}")
        
        # Ensure session is marked as accessed to extend its lifetime
        session.modified = True
        
        # Calculate statistics from database
        statistics = {}
        
        # Count total sevas booked by this user
        statistics['total_sevas'] = seva_collection.count_documents({"user_id": user_id})
        
        # Count total donations made by this user
        # Ensure user_id is properly converted to ObjectId for MongoDB queries
        statistics['total_donations'] = donations_collection.count_documents({
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"user_id": user_id}  # Also check for string user_id for backwards compatibility
            ]
        })
        
        # Calculate total amount donated by this user
        # Use aggregation to get the sum directly from MongoDB
        try:
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"user_id": ObjectId(user_id)},
                            {"user_id": user_id}
                        ]
                    }
                },
                {
                    "$addFields": {
                        "amount_numeric": {
                            "$cond": {
                                "if": {"$isNumber": "$amount"},
                                "then": "$amount",
                                "else": {"$toDouble": {"$ifNull": ["$amount", "0"]}}
                            }
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount_numeric"}
                    }
                }
            ]
            
            total_amount_result = list(donations_collection.aggregate(pipeline))
            total_amount = total_amount_result[0]['total'] if total_amount_result else 0
        except Exception as e:
            app.logger.error(f"Error calculating total donation amount: {str(e)}")
            # Fallback to the slower but safer method if aggregation fails
            donations_cursor = donations_collection.find({
                "$or": [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": user_id}
                ]
            })
            
            total_amount = 0
            for donation in donations_cursor:
                try:
                    amount = donation.get('amount', 0)
                    if amount:
                        total_amount += float(amount)
                except (ValueError, TypeError) as e:
                    app.logger.warning(f"Skipping invalid amount: {amount} - {str(e)}")
        
        statistics['total_amount'] = total_amount
        
        # Create monthly activity data - initialize with zeros
        monthly_activity = [0] * 12
        current_year = datetime.now().year
        
        # Get donations by month using both date fields
        for month in range(1, 13):
            month_pattern = f"{current_year}-{month:02d}"
            month_donations = donations_collection.count_documents({
                "$or": [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": user_id}
                ],
                "$or": [
                    {"date": {"$regex": month_pattern}},
                    {"created_at": {"$regex": month_pattern}}
                ]
            })
            
            # Get sevas by month
            month_sevas = seva_collection.count_documents({
                "user_id": user_id,
                "booking_date": {"$regex": month_pattern}
            })
            
            # Update the activity count for this month (0-indexed array)
            monthly_activity[month-1] = month_donations + month_sevas
        
        statistics['monthly_activity'] = monthly_activity
        
        # Get current date as string for comparison with database
        current_date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Get recent donations
        recent_donations = list(donations_collection.find({
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"user_id": user_id}
            ]
        }).sort([("date", -1), ("created_at", -1)]).limit(5))
        
        # Process donations for display in template
        for donation in recent_donations:
            if '_id' in donation:
                donation['_id'] = str(donation['_id'])
            
            # Convert user_id to string if it's an ObjectId
            if 'user_id' in donation and isinstance(donation['user_id'], ObjectId):
                donation['user_id'] = str(donation['user_id'])
                
            # Ensure date consistency
            if 'date' not in donation and 'created_at' in donation:
                donation['date'] = donation['created_at']
                
            # Format donation date for template
            if 'date' in donation:
                # For the donation_date field expected in the template
                if isinstance(donation['date'], datetime):
                    donation['donation_date'] = donation['date']
                else:
                    try:
                        donation['donation_date'] = datetime.fromisoformat(str(donation['date']).replace('Z', '+00:00'))
                    except:
                        donation['donation_date_str'] = str(donation['date'])
                        
            # Set purpose field from various possible sources
            if 'purpose' not in donation:
                donation['purpose'] = donation.get('donation_type_name', donation.get('donation_type', 'General Donation'))
        
        # Get upcoming sevas
        upcoming_sevas = list(seva_collection.find({
            "user_id": user_id,
            "seva_date": {"$gte": current_date_str},
            "status": {"$ne": "completed"}
        }).sort("seva_date", 1))
        
        # Convert ObjectIds to strings for the template and handle dates
        for seva in upcoming_sevas:
            if '_id' in seva:
                seva['_id'] = str(seva['_id'])
            
            # Ensure seva_date is a datetime object for the template
            if 'seva_date' in seva and not isinstance(seva['seva_date'], datetime):
                # Store the original string date
                seva['seva_date_str'] = seva['seva_date']
                # Try to convert string to datetime if needed by template
                try:
                    seva['seva_date'] = datetime.strptime(seva['seva_date'], '%Y-%m-%d')
                except (ValueError, TypeError):
                    # If conversion fails, keep as is - templates will need to handle string dates
                    pass
        
        # Fetch active donation goals for display
        active_goals = list(donation_goals_collection.find({"is_active": True}))
        for goal in active_goals:
            if '_id' in goal:
                goal['_id'] = str(goal['_id'])
                
            # Ensure we have correct amounts
            goal['target_amount'] = float(goal.get('target_amount', 0))
            goal['current_amount'] = float(goal.get('current_amount', 0))
            
        # Fetch upcoming events if available
        upcoming_events = []
        try:
            # Get current date as datetime object
            today_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_str = today_dt.strftime('%Y-%m-%d')
            
            # Query for events where date is either:
            # 1. A datetime object greater than or equal to today
            # 2. A string date that we can parse that's greater than or equal to today
            upcoming_events_cursor = events_collection.find({
                "$or": [
                    {"date": {"$gte": today_dt}},  # For datetime objects
                    {"date": {"$gte": today_str}}  # For string dates in YYYY-MM-DD format
                ]
            }).sort("date", 1).limit(3)
            
            upcoming_events = list(upcoming_events_cursor)
            
            # Process events to ensure dates are proper datetime objects
            for event in upcoming_events:
                if '_id' in event:
                    event['_id'] = str(event['_id'])
                
                # Convert date string to datetime if needed
                if 'date' in event and isinstance(event['date'], str):
                    try:
                        event['date'] = datetime.strptime(event['date'], '%Y-%m-%d')
                    except (ValueError, TypeError):
                        # Try alternative format
                        try:
                            event['date'] = datetime.strptime(event['date'], '%d-%m-%Y')
                        except (ValueError, TypeError):
                            # Default to today if parsing fails
                            event['date'] = today_dt
            
            app.logger.debug(f"Found {len(upcoming_events)} upcoming events for dashboard")
        except Exception as e:
            app.logger.error(f"Error fetching upcoming events: {str(e)}", exc_info=True)
            # Continue with empty events list if there's an error
        
        return render_template(
            "user/dashboard.html",
            user=user_data,
            statistics=statistics,
            upcoming_sevas=upcoming_sevas,
            recent_donations=recent_donations,
            active_goals=active_goals,
            upcoming_events=upcoming_events
        )
    except Exception as e:
        app.logger.error(f"Error in dashboard: {str(e)}", exc_info=True)
        flash("An error occurred while loading the dashboard.", "danger")
        return redirect(url_for('user.login'))


# ----------------------------------
#  FORGOT PASSWORD (OTP-Based)
# ----------------------------------

@user_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    # Log the current session state and CSRF token
    app.logger.debug(f"Session in forgot_password: {dict(session)}")
    app.logger.debug(f"CSRF Token from form: {request.form.get('csrf_token', 'Not in form')}")
    app.logger.debug(f"CSRF Token in session: {session.get('csrf_token', 'Not in session')}")
    
    if request.method == "POST":
        email = request.form.get("email")
        
        # Debug log to see what email was submitted
        app.logger.debug(f"Forgot password request for email: {email}")
        
        # Check if user exists
        user = user_collection.find_one({"email": email})
        
        if not user:
            flash('Email not found!', 'danger')
            return render_template('user/forgot_password.html')
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=6))
        
        # Store OTP in MongoDB with expiration time (10 minutes from now)
        expiration_time = time.time() + 600  # 10 minutes in seconds
        
        user_collection.update_one(
            {"email": email},
            {"$set": {
                "reset_otp": otp,
                "reset_otp_time": expiration_time,
                "reset_otp_verified": False
            }}
        )
        
        # Store email in session as a backup, but we'll use URL params too
        session['email'] = email
        session.modified = True
        
        app.logger.debug(f"OTP generated: {otp} for email: {email}")
        app.logger.debug(f"OTP stored in MongoDB for user: {email}")
        
        # Send OTP via email
        try:
            send_otp_email(email, otp)
            app.logger.debug(f"OTP email sent to: {email}")
            flash('OTP sent to your email. Please check your inbox.', 'success')
            # Redirect with email parameter to make it more robust
            return redirect(url_for('user.verify_otp', email=email))
        except Exception as e:
            app.logger.error(f"Failed to send OTP email: {str(e)}")
            flash('Failed to send OTP. Please try again.', 'danger')
            return render_template('user/forgot_password.html')
    
    return render_template('user/forgot_password.html')


def send_otp_email(email, otp):
    """Send OTP email and return True if successful, False otherwise"""
    subject = "Your Password Reset OTP"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #FF7F00;">Password Reset OTP</h2>
        <p>You requested to reset your password. Use the following OTP to continue:</p>
        <div style="background-color: #f7f7f7; padding: 15px; font-size: 24px; text-align: center; letter-spacing: 5px; font-weight: bold; margin: 20px 0;">
            {otp}
        </div>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you did not request a password reset, please ignore this email or contact support.</p>
        <p>Thank you,<br>Temple Management Team</p>
    </div>
    """

    msg = Message(subject, sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[email])
    msg.html = html_content
    msg.body = f"Your OTP for password reset is: {otp}. It expires in 10 minutes."

    try:
        # Log mail settings before sending
        logger.debug(f"Sending mail with: SERVER={app.config.get('MAIL_SERVER')}, PORT={app.config.get('MAIL_PORT')}")
        logger.debug(f"Using credentials: USERNAME={app.config.get('MAIL_USERNAME')}, SENDER={app.config.get('MAIL_DEFAULT_SENDER')}")
        
        mail.send(msg)
        logger.info(f"OTP email sent successfully to {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {str(e)}")
        print(f"Error sending OTP email: {e}")
        return False


# ----------------------------------
#  VERIFY OTP
# ----------------------------------

@user_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    # Add more detailed debug logging
    app.logger.debug(f"verify_otp route called. Method: {request.method}")
    app.logger.debug(f"Session state at verify_otp: {dict(session)}")
    app.logger.debug(f"Request args: {dict(request.args)}")
    
    # Check if email is in query parameters (for token-based approach)
    email = request.args.get('email') or session.get('email')
    
    if not email:
        app.logger.warning("No email in session or parameters, redirecting to forgot_password")
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('user.forgot_password'))
    
    # Store email in session as backup
    session['email'] = email
    session.modified = True
    
    # Get user from database
    user = user_collection.find_one({"email": email})
    if not user:
        app.logger.warning(f"User not found for email: {email}")
        flash('User not found. Please try again.', 'danger')
        return redirect(url_for('user.forgot_password'))
    
    # Check if OTP exists and has not expired
    current_time = time.time()
    if 'reset_otp_time' not in user or current_time > user['reset_otp_time']:
        app.logger.warning(f"OTP expired or not found for email: {email}")
        flash('OTP has expired. Please request a new one.', 'danger')
        return redirect(url_for('user.forgot_password'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = user.get('reset_otp')
        
        app.logger.debug(f"OTP entered: {entered_otp}")
        app.logger.debug(f"Stored OTP in MongoDB: {stored_otp}")
        
        # Validate OTP format first
        if not entered_otp or not entered_otp.isdigit() or len(entered_otp) != 6:
            flash('OTP must be a 6-digit number. Please check and try again.', 'warning')
            return render_template('user/verify_otp.html', email=email)
        
        # Get failed attempts counter or initialize to zero
        failed_attempts = user.get('otp_failed_attempts', 0)
        
        # Check if OTP is correct
        if stored_otp and entered_otp == stored_otp:
            app.logger.debug("OTP verification successful")
            
            # Mark user as OTP verified in MongoDB
            user_collection.update_one(
                {"email": email},
                {"$set": {"reset_otp_verified": True}}
            )
            
            # Create a secure token that includes the email for the reset password page
            token = secrets.token_urlsafe(32)
            user_collection.update_one(
                {"email": email},
                {"$set": {"reset_token": token}}
            )
            
            # Redirect to reset password with token
            return redirect(url_for('user.reset_password', token=token))
        
        # OTP is incorrect
        app.logger.warning("Invalid OTP entered")
        
        # Increment failed attempts counter (max 5 attempts)
        failed_attempts += 1
        
        # Update failed attempts in database
        user_collection.update_one(
            {"email": email},
            {"$set": {"otp_failed_attempts": failed_attempts}}
        )
        
        # Different messages based on number of failed attempts
        if failed_attempts >= 5:
            # Generate new OTP after 5 failed attempts
            otp = ''.join(random.choices('0123456789', k=6))
            expiration_time = time.time() + 600  # 10 minutes in seconds
            
            # Update OTP in database
            user_collection.update_one(
                {"email": email},
                {"$set": {
                    "reset_otp": otp,
                    "reset_otp_time": expiration_time,
                    "otp_failed_attempts": 0
                }}
            )
            
            # Send new OTP
            try:
                send_otp_email(email, otp)
                flash('Too many failed attempts. A new OTP has been sent to your email.', 'warning')
            except Exception as e:
                app.logger.error(f"Failed to send new OTP after failed attempts: {str(e)}")
                flash('Failed to send a new OTP. Please try again later.', 'danger')
        else:
            remaining_attempts = 5 - failed_attempts
            flash(f'Invalid OTP. Please try again. {remaining_attempts} attempts remaining.', 'danger')
    
    return render_template('user/verify_otp.html', email=email)


# ----------------------------------
#  RESET PASSWORD
# ----------------------------------

@user_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    # Add more detailed debug logging
    app.logger.debug(f"reset_password route called. Method: {request.method}")
    app.logger.debug(f"Session state at reset_password: {dict(session)}")
    app.logger.debug(f"Request args: {dict(request.args)}")
    
    # Get token from query parameters or form data
    token = request.args.get('token') or request.form.get('token')
    email = session.get('email') or request.form.get('email')
    
    app.logger.debug(f"Token from request: {token}")
    app.logger.debug(f"Email from request: {email}")
    
    # Try to find user by token first (more secure)
    user = None
    if token:
        user = user_collection.find_one({"reset_token": token})
        if user:
            email = user['email']
            # Update session with email
            session['email'] = email
            session.modified = True
    
    # If no token or token invalid, try session email
    if not user and email:
        user = user_collection.find_one({"email": email})
    
    # If still no user, redirect to forgot password
    if not user:
        app.logger.warning("No valid token or email in session, redirecting to forgot_password")
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('user.forgot_password'))
    
    # Check if user has verified OTP
    if not user.get('reset_otp_verified', False):
        app.logger.warning(f"OTP not verified for user: {email}")
        flash('Please verify your OTP first.', 'danger')
        return redirect(url_for('user.verify_otp', email=email))
    
    # Check if OTP has expired
    current_time = time.time()
    if 'reset_otp_time' not in user or current_time > user['reset_otp_time']:
        app.logger.warning(f"OTP expired for email: {email}")
        flash('Your session has expired. Please request a new OTP.', 'danger')
        return redirect(url_for('user.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        app.logger.debug(f"Password reset attempt for email: {email}")
        
        # Validate passwords
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('user/reset_password.html', email=email)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('user/reset_password.html', email=email)
        
        # Check if new password is the same as the old one
        stored_password = user.get("password", "")
        if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            flash('New password cannot be the same as your old password.', 'danger')
            return render_template('user/reset_password.html', email=email)
        
        # Update password in database
        try:
            # Fix: Use consistent bcrypt method as register route
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            user_collection.update_one(
                {"email": email},
                {"$set": {"password": hashed_password},
                 "$unset": {"reset_otp": "", "reset_otp_time": "", "reset_otp_verified": "", "reset_token": ""}}
            )
            
            app.logger.debug(f"Password reset successful for email: {email}")
            
            # Clear email from session
            session.pop('email', None)
            
            flash('Password has been reset successfully. Please login.', 'success')
            return redirect(url_for('user.login', reset='success'))
        except Exception as e:
            app.logger.error(f"Password reset failed: {str(e)}")
            flash('Failed to reset password. Please try again.', 'danger')
    
    return render_template('user/reset_password.html', email=email)


@user_bp.route("/profile")
@login_required
def profile():
    # Add explicit logging to check session contents
    app.logger.debug(f"Session content in profile route: {session}")
    
    # Make sure user is in session
    if 'user' in session:
        user_data = session['user']
        try:
            # Make sure session is refreshed/updated
            session.modified = True
            
            # Get the user details from database
            user_details = user_collection.find_one({"_id": ObjectId(user_data['id'])})
            
            if user_details:
                app.logger.debug(f"User details found: {user_details.get('name')}")
                
                # Convert ObjectIds to strings for the template
                user_details['_id'] = str(user_details['_id'])
                
                # Calculate user statistics
                statistics = {}
                
                # Total sevas booked
                statistics['total_sevas'] = seva_collection.count_documents({"user_id": user_data['id']})
                
                # Total donations - check for both ObjectId and string user_id
                statistics['total_donations'] = donations_collection.count_documents({
                    "$or": [
                        {"user_id": ObjectId(user_data['id'])},
                        {"user_id": user_data['id']}  # Also check for string user_id for backwards compatibility
                    ]
                })
                
                # Calculate total amount donated - use aggregation for better performance
                try:
                    pipeline = [
                        {
                            "$match": {
                                "$or": [
                                    {"user_id": ObjectId(user_data['id'])},
                                    {"user_id": user_data['id']}
                                ]
                            }
                        },
                        {
                            "$addFields": {
                                "amount_numeric": {
                                    "$cond": {
                                        "if": {"$isNumber": "$amount"},
                                        "then": "$amount",
                                        "else": {"$toDouble": {"$ifNull": ["$amount", "0"]}}
                                    }
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": "$amount_numeric"}
                            }
                        }
                    ]
                    
                    total_amount_result = list(donations_collection.aggregate(pipeline))
                    total_amount = total_amount_result[0]['total'] if total_amount_result else 0
                except Exception as e:
                    app.logger.error(f"Error calculating total donation amount in profile: {str(e)}")
                    # Fallback to the slower but safer method if aggregation fails
                    donations_cursor = donations_collection.find({
                        "$or": [
                            {"user_id": ObjectId(user_data['id'])},
                            {"user_id": user_data['id']}
                        ]
                    })
                    
                    total_amount = 0
                    for donation in donations_cursor:
                        try:
                            amount = donation.get('amount', 0)
                            if amount:
                                total_amount += float(amount)
                        except (ValueError, TypeError) as e:
                            app.logger.warning(f"Skipping invalid amount: {amount} - {str(e)}")
                
                statistics['total_amount'] = total_amount
                
                # Get current date as string for comparison with database
                current_date_str = datetime.now().strftime('%Y-%m-%d')
                
                # Calculate upcoming sevas
                statistics['upcoming_sevas'] = seva_collection.count_documents({
                    "user_id": user_data['id'],
                    "seva_date": {"$gte": current_date_str},
                    "status": {"$ne": "completed"}
                })
                
                # Recent activity - last 5 activities across donations and sevas
                recent_donations = list(donations_collection.find({
                    "$or": [
                        {"user_id": ObjectId(user_data['id'])},
                        {"user_id": user_data['id']}
                    ]
                }).sort([("date", -1), ("created_at", -1)]).limit(3))
                
                recent_sevas = list(seva_collection.find(
                    {"user_id": user_data['id']}
                ).sort("booking_date", -1).limit(3))
                
                activities = []
                
                # Add donations to activities
                for donation in recent_donations:
                    if '_id' in donation:
                        donation['_id'] = str(donation['_id'])
                    
                    # Convert user_id to string if it's an ObjectId
                    if 'user_id' in donation and isinstance(donation['user_id'], ObjectId):
                        donation['user_id'] = str(donation['user_id'])
                    
                    # Make sure donation date exists (might be in date or created_at)
                    if 'date' not in donation and 'created_at' in donation:
                        donation['date'] = donation['created_at']
                    
                    # Process donation data for template
                    if 'date' in donation:
                        # For the donation_date field expected in the template
                        if isinstance(donation['date'], datetime):
                            donation['donation_date'] = donation['date']
                        else:
                            try:
                                donation['donation_date'] = datetime.fromisoformat(str(donation['date']).replace('Z', '+00:00'))
                            except:
                                donation['donation_date_str'] = str(donation['date'])
                    
                    # Set purpose field from various possible sources
                    if 'purpose' not in donation:
                        donation['purpose'] = donation.get('donation_type_name', donation.get('donation_type', 'General Donation'))
                    
                    # Make sure transaction_id is available for receipt download
                    if 'transaction_id' not in donation and 'payment_id' in donation:
                        donation['transaction_id'] = donation['payment_id']
                    
                    activities.append({
                        'type': 'donation',
                        'date': donation.get('donation_date', donation.get('date')),
                        'amount': donation.get('amount', 0),
                        'cause': donation.get('purpose', donation.get('donation_type_name', 'General Donation'))
                    })
                
                # Add sevas to activities
                for seva in recent_sevas:
                    if '_id' in seva:
                        seva['_id'] = str(seva['_id'])
                    activities.append({
                        'type': 'seva',
                        'date': seva.get('booking_date'),
                        'name': seva.get('seva_name', 'Unknown Seva'),
                        'status': seva.get('status', 'pending')
                    })
                
                # Sort by date (most recent first) and take top 5
                activities.sort(key=lambda x: x['date'] if x['date'] else '1900-01-01', reverse=True)
                activities = activities[:5]
                
                statistics['recent_activity'] = activities
                
                # Monthly activity summary - example data
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                # Create a comprehensive monthly activity dataset
                monthly_activity_data = []
                
                # Get data for the past 12 months
                for i in range(12):
                    # Calculate the month and year (going backwards from current month)
                    month = ((current_month - i - 1) % 12) + 1  # Convert 0 to 12 for December
                    year = current_year if month <= current_month else current_year - 1
                    
                    # Format for MongoDB query
                    month_pattern = f"{year}-{month:02d}"
                    
                    # Count donations for this month
                    month_donations = donations_collection.count_documents({
                        "$or": [
                            {"user_id": ObjectId(user_data['id'])},
                            {"user_id": user_data['id']}
                        ],
                        "$or": [
                            {"date": {"$regex": month_pattern}},
                            {"created_at": {"$regex": month_pattern}}
                        ]
                    })
                    
                    # Count sevas for this month
                    month_sevas = seva_collection.count_documents({
                        "user_id": user_data['id'],
                        "booking_date": {"$regex": month_pattern}
                    })
                    
                    # Get donation amounts for this month
                    amount_pipeline = [
                        {
                            "$match": {
                                "$or": [
                                    {"user_id": ObjectId(user_data['id'])},
                                    {"user_id": user_data['id']}
                                ],
                                "$or": [
                                    {"date": {"$regex": month_pattern}},
                                    {"created_at": {"$regex": month_pattern}}
                                ]
                            }
                        },
                        {
                            "$addFields": {
                                "amount_numeric": {
                                    "$cond": {
                                        "if": {"$isNumber": "$amount"},
                                        "then": "$amount",
                                        "else": {"$toDouble": {"$ifNull": ["$amount", "0"]}}
                                    }
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": "$amount_numeric"}
                            }
                        }
                    ]
                    
                    try:
                        amount_result = list(donations_collection.aggregate(amount_pipeline))
                        month_amount = amount_result[0]['total'] if amount_result else 0
                    except Exception as e:
                        app.logger.error(f"Error calculating monthly donation amount: {str(e)}")
                        month_amount = 0
                    
                    # Add data for this month
                    monthly_activity_data.append({
                        'month': month,
                        'year': year,
                        'month_name': datetime(year, month, 1).strftime('%b'),
                        'donations': month_donations,
                        'sevas': month_sevas,
                        'total': month_donations + month_sevas,
                        'amount': month_amount
                    })
                
                # Reverse the list to get chronological order (oldest to newest)
                monthly_activity_data.reverse()
                
                # Extract arrays for chart display
                donation_counts = [month_data['donations'] for month_data in monthly_activity_data]
                seva_counts = [month_data['sevas'] for month_data in monthly_activity_data]
                total_counts = [month_data['total'] for month_data in monthly_activity_data]
                donation_amounts = [month_data['amount'] for month_data in monthly_activity_data]
                month_labels = [month_data['month_name'] for month_data in monthly_activity_data]
                
                # Store in statistics for the template
                statistics['monthly_activity'] = {
                    'data': monthly_activity_data,
                    'donations': donation_counts,
                    'sevas': seva_counts,
                    'total': total_counts,
                    'amounts': donation_amounts,
                    'labels': month_labels
                }
                
                return render_template("user/profile.html", 
                                      user=user_details, 
                                      statistics=statistics, 
                                      recent_sevas=recent_sevas, 
                                      recent_donations=recent_donations)
            else:
                app.logger.error(f"User details not found for ID: {user_data['id']}")
        except Exception as e:
            app.logger.error(f"Error in profile route: {str(e)}", exc_info=True)
    else:
        app.logger.warning("User not in session - this should not happen with @login_required decorator")
    
    # If we got here, something went wrong
    flash("Unable to load profile. Please try logging in again.", "warning")
    return redirect(url_for("user.login"))

@user_bp.route("/edit-profile")
@login_required
def edit_profile():
    """Route to edit user profile"""
    if 'user' in session:
        user_data = session['user']
        try:
            # Make sure session is refreshed/updated
            session.modified = True
            
            # Get the user details from database
            user_details = user_collection.find_one({"_id": ObjectId(user_data['id'])})
            
            if user_details:
                # Convert ObjectId to string for template
                user_details['_id'] = str(user_details['_id'])
                return render_template("user/edit_profile.html", user=user_details)
            else:
                app.logger.error(f"User details not found for ID: {user_data['id']}")
        except Exception as e:
            app.logger.error(f"Error in edit_profile route: {str(e)}", exc_info=True)
    
    flash("Unable to load profile editor. Please try logging in again.", "warning")
    return redirect(url_for("user.login"))

@user_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    """Route to handle profile update form submission"""
    if 'user' in session:
        user_data = session['user']
        try:
            # Get form data
            name = request.form.get('name')
            phone = request.form.get('phone')
            birthdate = request.form.get('birthdate')
            address = request.form.get('address')
            email_notifications = 'email_notifications' in request.form
            sms_notifications = 'sms_notifications' in request.form
            
            # Update user in database
            user_collection.update_one(
                {"_id": ObjectId(user_data['id'])},
                {"$set": {
                    "name": name,
                    "phone": phone,
                    "birthdate": birthdate,
                    "address": address,
                    "email_notifications": email_notifications,
                    "sms_notifications": sms_notifications,
                    "updated_at": datetime.now()
                }}
            )
            
            # Update session data
            session['user']['name'] = name
            session.modified = True
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for("user.profile"))
        except Exception as e:
            app.logger.error(f"Error updating profile: {str(e)}", exc_info=True)
            flash("An error occurred while updating your profile. Please try again.", "danger")
    
    return redirect(url_for("user.edit_profile"))

@user_bp.route("/history")
@login_required
def history():
    user_data = session.get('user', {})
    if not user_data:
        flash("Please log in to view your history.", "warning")
        return redirect(url_for("user.login"))
        
    try:
        user_id = user_data.get('id')
        if not user_id:
            flash("User information is incomplete. Please log in again.", "warning")
            return redirect(url_for("user.login"))
        
        # Initialize empty lists
        seva_bookings = []
        donations = []
        combined_activity = []
        
        # Fetch user's seva bookings from MongoDB
        try:
            # Try using ObjectId if the ID is stored that way
            from bson import ObjectId
            try:
                object_id = ObjectId(user_id)
                seva_bookings = list(seva_collection.find({"user_id": object_id}).sort("booking_date", -1))
                
                # If no results, try with string ID
                if not seva_bookings:
                    seva_bookings = list(seva_collection.find({"user_id": user_id}).sort("booking_date", -1))
            except:
                # Fall back to string ID
                seva_bookings = list(seva_collection.find({"user_id": user_id}).sort("booking_date", -1))
                
            # Also try with email as a fallback
            if not seva_bookings and user_data.get('email'):
                seva_bookings = list(seva_collection.find({"email": user_data.get('email')}).sort("booking_date", -1))
                
            app.logger.debug(f"Found {len(seva_bookings)} seva bookings for user {user_id}")
        except Exception as e:
            app.logger.error(f"Error fetching seva bookings: {str(e)}", exc_info=True)
            seva_bookings = []
        
        # Fetch user's donations from MongoDB
        try:
            # Try using ObjectId if the ID is stored that way
            try:
                object_id = ObjectId(user_id)
                donations = list(donations_collection.find({"user_id": object_id}).sort([("date", -1), ("created_at", -1)]))
                
                # If no results, try with string ID
                if not donations:
                    donations = list(donations_collection.find({"user_id": user_id}).sort([("date", -1), ("created_at", -1)]))
            except:
                # Fall back to string ID
                donations = list(donations_collection.find({"user_id": user_id}).sort([("date", -1), ("created_at", -1)]))
                
            # Also try with email as a fallback
            if not donations and user_data.get('email'):
                donations = list(donations_collection.find({"email": user_data.get('email')}).sort([("date", -1), ("created_at", -1)]))
            
            app.logger.debug(f"Found {len(donations)} donations for user {user_id}")
        except Exception as e:
            app.logger.error(f"Error fetching donations: {str(e)}", exc_info=True)
            donations = []
        
        # Process seva bookings for display
        for seva in seva_bookings:
            if '_id' in seva:
                seva['_id'] = str(seva['_id'])
            
            # Ensure user_id is a string
            if 'user_id' in seva and isinstance(seva['user_id'], ObjectId):
                seva['user_id'] = str(seva['user_id'])
            
            # Handle seva_date formatting
            if 'seva_date' in seva:
                if isinstance(seva['seva_date'], datetime):
                    seva['seva_date_str'] = seva['seva_date'].strftime('%Y-%m-%d')
                else:
                    seva['seva_date_str'] = str(seva['seva_date'])
            elif 'date' in seva:
                if isinstance(seva['date'], datetime):
                    seva['seva_date'] = seva['date']
                    seva['seva_date_str'] = seva['date'].strftime('%Y-%m-%d')
                else:
                    seva['seva_date'] = seva['date']
                    seva['seva_date_str'] = str(seva['date'])
            
            # Add booking time if available or extract from created_at
            if 'booking_time' not in seva and 'created_at' in seva and isinstance(seva['created_at'], datetime):
                seva['booking_time'] = seva['created_at'].strftime('%H:%M')
            elif 'booking_time' not in seva and 'booking_date' in seva and isinstance(seva['booking_date'], datetime):
                seva['booking_time'] = seva['booking_date'].strftime('%H:%M')
            
            # Add timestamp for sorting
            if 'booking_timestamp' not in seva:
                booking_time = None
                if 'booking_date' in seva and isinstance(seva['booking_date'], datetime):
                    booking_time = seva['booking_date']
                elif 'seva_date' in seva and isinstance(seva['seva_date'], datetime):
                    booking_time = seva['seva_date']
                elif 'date' in seva and isinstance(seva['date'], datetime):
                    booking_time = seva['date']
                
                if booking_time:
                    seva['booking_timestamp'] = int(booking_time.timestamp())
            
            # Ensure amount is present
            if 'amount' not in seva:
                seva['amount'] = seva.get('seva_price', 0)
            
            
            # Ensure status is present
            if 'status' not in seva:
                seva['status'] = 'confirmed'  # Default status
        
        # Process donations for display
        for donation in donations:
            if '_id' in donation:
                donation['_id'] = str(donation['_id'])
            
            # Ensure user_id is a string
            if 'user_id' in donation and isinstance(donation['user_id'], ObjectId):
                donation['user_id'] = str(donation['user_id'])
            
            # Ensure date consistency
            if 'date' not in donation and 'created_at' in donation:
                donation['date'] = donation['created_at']
                
            # Process donation data for template display
            if 'date' in donation:
                # For the donation_date field expected in the template
                if isinstance(donation['date'], datetime):
                    donation['donation_date'] = donation['date']
                    donation['date_str'] = donation['date'].strftime('%Y-%m-%d')
                else:
                    try:
                        date_obj = datetime.fromisoformat(str(donation['date']).replace('Z', '+00:00'))
                        donation['donation_date'] = date_obj
                        donation['date_str'] = date_obj.strftime('%Y-%m-%d')
                    except:
                        donation['date_str'] = str(donation['date'])
            
            # Add time information
            if 'time' not in donation and 'created_at' in donation and isinstance(donation['created_at'], datetime):
                donation['time'] = donation['created_at'].strftime('%H:%M')
            elif 'time' not in donation and 'date' in donation and isinstance(donation['date'], datetime):
                donation['time'] = donation['date'].strftime('%H:%M')
                
            # Add timestamp for sorting
            if 'timestamp' not in donation:
                donation_time = None
                if 'date' in donation and isinstance(donation['date'], datetime):
                    donation_time = donation['date']
                elif 'created_at' in donation and isinstance(donation['created_at'], datetime):
                    donation_time = donation['created_at']
                
                if donation_time:
                    donation['timestamp'] = int(donation_time.timestamp())
                
            # Set purpose field from various possible sources
            if 'purpose' not in donation:
                donation['purpose'] = donation.get('donation_type_name', 
                                      donation.get('donation_type', 
                                      donation.get('type', 'General Donation')))
                
            # Make sure transaction_id is available for receipt download
            if 'transaction_id' not in donation and 'payment_id' in donation:
                donation['transaction_id'] = donation['payment_id']
            elif 'transaction_id' not in donation:
                donation['transaction_id'] = str(donation['_id'])
                
            # Ensure title is present
            if 'title' not in donation:
                donation['title'] = f"Donation - {donation.get('purpose', 'General')}"
                
            # Ensure status is present
            if 'status' not in donation:
                donation['status'] = 'completed'  # Default status
        
        # Create a combined activity feed sorted by date
        
        # Add seva bookings to combined activity
        for seva in seva_bookings:
            # Get the booking date
            booking_date = seva.get('booking_date', seva.get('seva_date', seva.get('date', datetime.now())))
            date_str = ''
            time_str = ''
            
            # Safe date conversion
            if isinstance(booking_date, datetime):
                date_str = booking_date.strftime('%Y-%m-%d')
                time_str = booking_date.strftime('%H:%M')
            else:
                date_str = str(booking_date)
            
            # Use booking_time if available
            if 'booking_time' in seva:
                time_str = seva['booking_time']
            
            combined_activity.append({
                'type': 'seva',
                'title': seva.get('seva_name', 'Seva Booking'),
                'description': f"{seva.get('seva_type', 'General')} - ₹{seva.get('amount', seva.get('seva_price', '0'))}",
                'date': date_str,
                'time': time_str,
                'timestamp': seva.get('booking_timestamp', 0),
                'status': seva.get('status', 'confirmed'),
                'id': str(seva.get('_id', '')),
            })
        
        # Add donations to combined activity
        for donation in donations:
            date = donation.get('created_at', donation.get('date', datetime.now()))
            date_str = ''
            time_str = ''
            
            # Safe date conversion
            if isinstance(date, datetime):
                date_str = date.strftime('%Y-%m-%d')
                time_str = date.strftime('%H:%M')
            else:
                date_str = str(date)
            
            # Use time if available
            if 'time' in donation:
                time_str = donation['time']
            
            combined_activity.append({
                'type': 'donation',
                'title': donation.get('title', f"Donation - {donation.get('purpose', 'General')}"),
                'description': f"Amount: ₹{donation.get('amount', '0')}",
                'date': date_str,
                'time': time_str,
                'timestamp': donation.get('timestamp', 0),
                'status': donation.get('status', 'completed'),
                'id': str(donation.get('_id', '')),
                'transaction_id': donation.get('transaction_id', ''),
            })
        
        # Sort combined activity by date (most recent first)
        combined_activity.sort(key=lambda x: (x['date'], x['time']), reverse=True)
        
        app.logger.debug(f"Rendering user history with {len(seva_bookings)} sevas, {len(donations)} donations, and {len(combined_activity)} combined activities")
        
        return render_template(
            "user/user_history.html", 
            user=user_data,
            seva_bookings=seva_bookings,
            donations=donations,
            combined_activity=combined_activity
        )
    except Exception as e:
        app.logger.error(f"Error in history route: {str(e)}", exc_info=True)
        flash("An error occurred while loading your history. Please try again later.", "danger")
        return redirect(url_for("user.dashboard"))


@user_bp.route("/check-auth")
def check_auth():
    """Check if user is authenticated"""
    try:
        is_authenticated = 'user' in session
        return jsonify({
            "is_authenticated": is_authenticated,
            "user": session.get('user', {}) if is_authenticated else None
        })
    except Exception as e:
        app.logger.error(f"Error checking authentication: {str(e)}")
        return jsonify({"is_authenticated": False, "error": "Error checking authentication status"}), 500


@user_bp.route("/donations/submit", methods=["POST"])
@login_required
def process_donation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        # Validate required fields
        required_fields = ["donationId", "amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400

        # Validate amount
        try:
            amount = float(data["amount"])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        # Get donation type name
        donation_type_id = data["donationId"]
        donation_type_name = donation_type_id  # Default to ID if not found
        
        # Try to get donation type name from database
        donation_type_doc = donations_list.find_one({"donation_id": donation_type_id})
        if donation_type_doc and 'donation_name' in donation_type_doc:
            donation_type_name = donation_type_doc['donation_name']

        # Create donation record
        donation = {
            "user_id": ObjectId(session["user"]["id"]),
            "donation_type": donation_type_id,
            "donation_type_name": donation_type_name,
            "amount": amount,
            "is_recurring": data.get("isRecurring", False),
            "is_anonymous": data.get("isAnonymous", False),
            "status": "completed",
            "transaction_id": secrets.token_hex(8),
            "date": datetime.now(),               # Use date instead of created_at
            "created_at": datetime.now(),         # Keep created_at for backward compatibility
            "donor_name": session["user"].get("name", "Anonymous"),
            "email": session["user"].get("email", "")
        }

        # Insert into database
        result = donations_collection.insert_one(donation)

        if result.inserted_id:
            return jsonify({
                "success": True,
                "data": {
                    "transactionId": donation["transaction_id"],
                    "date": donation["date"].strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": amount
                }
            })
        else:
            raise Exception("Failed to save donation")
        
    except Exception as e:
        app.logger.error(f"Donation processing error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while processing your donation"
        }), 500

@user_bp.route("/donation-details/<transaction_id>")
@login_required
def get_donation_details(transaction_id):
    try:
        # Fetch donation details from database
        donation = donations_collection.find_one({"transaction_id": transaction_id})
        
        if not donation:
            return jsonify({
                "success": False,
                "message": "Donation not found"
            }), 404

        # Check if user has permission to view this donation
        if str(donation["user_id"]) != session["user"]["id"] and not donation.get("is_anonymous"):
            return jsonify({
                "success": False,
                "message": "Unauthorized to view this donation"
            }), 403

        # Format donation details
        donation_details = {
            "transaction_id": donation["transaction_id"],
            "date": donation["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "amount": donation["amount"],
            "type": donation["donation_type"],
            "status": donation["status"],
            "donor_name": "Anonymous" if donation.get("is_anonymous") else session["user"]["name"],
            "email": session["user"]["email"] if not donation.get("is_anonymous") else "Anonymous",
            "purpose": donation.get("purpose", "General Donation"),
            "notes": donation.get("notes", "")
        }
        
        return jsonify({
            "success": True,
            "data": donation_details
        })
            
    except Exception as e:
        app.logger.error(f"Error fetching donation details: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error retrieving donation details"
        }), 500

@user_bp.route("/quick-donate", methods=["POST"])
@login_required
def quick_donate():
    try:
        goal_title = request.form.get("goal_title")
        amount = float(request.form.get("amount", 0))

        if not goal_title or amount <= 0:
            return jsonify({
                "success": False,
                "message": "Invalid donation parameters"
            }), 400

        # Create quick donation record
        donation = {
            "user_id": ObjectId(session["user"]["id"]),
            "donation_type": "quick",
            "goal_title": goal_title,
            "amount": amount,
            "status": "completed",
            "transaction_id": secrets.token_hex(8),
            "created_at": datetime.utcnow()
        }

        result = donations_collection.insert_one(donation)

        if result.inserted_id:
            # Calculate new goal progress
            total_donations = donations_collection.find({
                "goal_title": goal_title,
                "status": "completed"
            })
            current_amount = sum(d["amount"] for d in total_donations)
            
            return jsonify({
                "status": "success", 
                "data": {
                    "transactionId": donation["transaction_id"],
                    "date": donation["created_at"].strftime("%Y-%m-%d"),
                    "current": current_amount,
                    "percentage": min(int((current_amount / 100000) * 100), 100)  # Assuming goal is 1,00,000
                }
            })

        return jsonify({
            "status": "error",
            "message": "Failed to process donation"
        }), 500
            
    except Exception as e:
        app.logger.error(f"Quick donation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing your donation"
        }), 500

@user_bp.route("/debug-session")
@login_required
def debug_session():
    """Route to debug session configuration and state."""
    session_info = {
        "user_in_session": "user" in session,
        "session_permanent": session.permanent if hasattr(session, "permanent") else "Not set",
        "session_modified": session.modified if hasattr(session, "modified") else "Not available",
        "session_new": session.new if hasattr(session, "new") else "Not available",
        "session_sid": session.sid if hasattr(session, "sid") else "Not available"
    }
    
    # Add Flask app configuration related to sessions
    config_info = {
        "SECRET_KEY_SET": app.secret_key is not None,
        "PERMANENT_SESSION_LIFETIME": app.config.get("PERMANENT_SESSION_LIFETIME", "Not set"),
        "SESSION_TYPE": app.config.get("SESSION_TYPE", "Not set"),
        "SESSION_PERMANENT": app.config.get("SESSION_PERMANENT", "Not set"),
        "SESSION_USE_SIGNER": app.config.get("SESSION_USE_SIGNER", "Not set"),
        "SESSION_FILE_DIR": app.config.get("SESSION_FILE_DIR", "Not set"),
        "SESSION_FILE_THRESHOLD": app.config.get("SESSION_FILE_THRESHOLD", "Not set"),
        "SESSION_COOKIE_NAME": app.config.get("SESSION_COOKIE_NAME", "Not set"),
        "SESSION_COOKIE_DOMAIN": app.config.get("SESSION_COOKIE_DOMAIN", "Not set"),
        "SESSION_COOKIE_PATH": app.config.get("SESSION_COOKIE_PATH", "Not set"),
        "SESSION_COOKIE_HTTPONLY": app.config.get("SESSION_COOKIE_HTTPONLY", "Not set"),
        "SESSION_COOKIE_SECURE": app.config.get("SESSION_COOKIE_SECURE", "Not set"),
        "SESSION_COOKIE_SAMESITE": app.config.get("SESSION_COOKIE_SAMESITE", "Not set")
    }
    
    # Log all the information
    app.logger.debug(f"Session debug information: {session_info}")
    app.logger.debug(f"Session configuration: {config_info}")
    
    # If user is in session, show their details
    user_data = None
    if "user" in session:
        user_data = session["user"]
        app.logger.debug(f"User in session: {user_data}")
    
    # Return information as JSON for easy debugging
    return jsonify({
        "session_info": session_info,
        "config_info": config_info,
        "user_data": user_data,
        "cookies": {key: request.cookies.get(key) for key in request.cookies}
    })

@user_bp.route("/resend_verification/<email>")
def resend_verification(email):
    """Resend verification OTP to unverified users"""
    try:
        app.logger.info(f"Resend verification requested for email: {email}")
        # Find the user
        user = user_collection.find_one({"email": email})
        
        if not user:
            app.logger.error(f"User not found for resend verification: {email}")
            flash("User not found!", "danger")
            return redirect(url_for("user.login"))
        
        # Check if already verified
        if user.get("verified", False):
            app.logger.info(f"User already verified: {email}")
            flash("Your email is already verified. Please log in.", "info")
            return redirect(url_for("user.login"))
        
        # Generate a new OTP
        otp = ''.join(random.choices('0123456789', k=6))
        expiration_time = time.time() + 600  # 10 minutes in seconds
        
        # Update the OTP in the database
        user_collection.update_one(
            {"email": email},
            {"$set": {
                "registration_otp": otp,
                "registration_otp_time": expiration_time
            }}
        )
        
        # Store email in session as a backup
        session['email'] = email
        session.modified = True
        
        # Send verification OTP
        app.logger.debug(f"Sending verification OTP to {email}")
        success = send_registration_otp(email, otp)
        
        if success:
            app.logger.info(f"Verification OTP resent successfully to: {email}")
            flash("Verification OTP has been sent to your email. Please check your inbox.", "success")
        else:
            app.logger.error(f"Failed to send verification OTP to: {email}")
            flash("Failed to send verification OTP. Please try again later.", "danger")
        
        return redirect(url_for("user.verify_registration_otp", email=email))
        
    except Exception as e:
        app.logger.error(f"Error resending verification OTP: {str(e)}", exc_info=True)
        flash("Failed to resend verification OTP. Please try again later.", "danger")
        return redirect(url_for("user.login"))

@user_bp.route("/manual-verify/<user_id>")
def manual_verify(user_id):
    """Manually verify a user account by ID - use only for fixing verification issues"""
    try:
        # Convert string ID to ObjectId
        user_object_id = ObjectId(user_id)
        
        # Find the user by ID
        user = user_collection.find_one({"_id": user_object_id})
        
        if not user:
            app.logger.error(f"User not found for manual verification: {user_id}")
            flash("User not found!", "danger")
            return redirect(url_for("user.login"))
        
        # Update user to verified status
        result = user_collection.update_one(
            {"_id": user_object_id},
            {"$set": {"verified": True}, "$unset": {"token": ""}}
        )
        
        # Log the update result
        app.logger.info(f"Manual verification for user ID {user_id}: matched={result.matched_count}, modified={result.modified_count}")
        
        # Double-check verification status
        updated_user = user_collection.find_one({"_id": user_object_id})
        verified_status = updated_user.get('verified', False)
        app.logger.info(f"After manual verification, status is: {verified_status}")
        
        if verified_status:
            flash(f"User {user.get('name')} ({user.get('email')}) has been manually verified.", "success")
        else:
            flash(f"Verification attempt completed but status check shows user is still unverified. Please check database.", "warning")
        
        return redirect(url_for("user.login"))
        
    except Exception as e:
        app.logger.error(f"Error in manual verification: {str(e)}", exc_info=True)
        flash("Failed to manually verify user. Please check server logs.", "danger")
        return redirect(url_for("user.login"))

@user_bp.route("/direct-verify/<email>")
def direct_verify_email(email):
    """Directly verify a user by their email - for troubleshooting verification issues only"""
    try:
        app.logger.debug(f"Direct verification attempted for email: {email}")
        
        # Find the user in the database
        user = user_collection.find_one({"email": email})
        
        if not user:
            app.logger.error(f"User not found with email: {email}")
            flash("User not found with this email.", "danger")
            return redirect(url_for("user.login"))
        
        # Update user to verified status
        result = user_collection.update_one(
            {"email": email},
            {"$set": {"verified": True}, "$unset": {"token": ""}}
        )
        
        # Log the update result
        app.logger.info(f"Direct verification result for {email}: matched={result.matched_count}, modified={result.modified_count}")
        
        # Double-check verification status
        updated_user = user_collection.find_one({"email": email})
        is_verified = updated_user.get('verified', False)
        
        if is_verified:
            flash(f"Email {email} has been verified successfully. You can now log in.", "success")
        else:
            app.logger.error(f"Direct verification failed for {email}: status after update = {is_verified}")
            flash("Verification failed. Please contact support.", "danger")
        
        return redirect(url_for("user.login"))
        
    except Exception as e:
        app.logger.error(f"Error in direct verification: {str(e)}", exc_info=True)
        flash("An error occurred during verification. Please try again.", "danger")
        return redirect(url_for("user.login"))

@user_bp.route("/activity-details/<type>/<id>")
@login_required
def activity_details(type, id):
    try:
        # Make sure user is in session
        if 'user' not in session:
            return jsonify({"error": "User not authenticated"}), 401
        
        user_data = session['user']
        user_id = user_data['id']
        
        # Fetch the details based on type
        if type == 'seva':
            # Get the seva details
            seva = seva_collection.find_one({"_id": ObjectId(id), "user_id": user_id})
            
            if not seva:
                return jsonify({"error": "Seva not found or access denied"}), 404
            
            # Format the content for the modal
            title = seva.get('seva_name', 'Seva Details')
            
            # Build HTML content using standard string concatenation
            content = '<div class="activity-details">'
            content += '<div class="details-item"><span class="details-label">Seva Type:</span>'
            content += '<span class="details-value">' + str(seva.get('seva_type', 'N/A')) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Date:</span>'
            content += '<span class="details-value">' + str(seva.get('seva_date_str', seva.get('seva_date', 'N/A'))) + '</span></div>'
            
            # Get amount with fallback to seva_price, similar to history route
            amount = seva.get('amount', seva.get('seva_price', 0))
            content += '<div class="details-item"><span class="details-label">Amount:</span>'
            content += '<span class="details-value">₹' + str(amount) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Status:</span>'
            content += '<span class="details-value">' + str(seva.get('status', 'N/A')) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Booking ID:</span>'
            content += '<span class="details-value">' + str(seva.get('_id', 'N/A')) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Transaction ID:</span>'
            content += '<span class="details-value">' + str(seva.get('transaction_id', 'N/A')) + '</span></div>'
            
            content += '</div>'
            
            return jsonify({"title": title, "content": content})
            
        elif type == 'donation':
            # Get the donation details using both ObjectId and string variants for compatibility
            donation = donations_collection.find_one({
                "_id": ObjectId(id),
                "$or": [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": user_id}
                ]
            })
            
            if not donation:
                return jsonify({"error": "Donation not found or access denied"}), 404
            
            # Format the content for the modal
            title = donation.get('title', 'Donation Details')
            
            # Get the date in a consistent format
            donation_date = "N/A"
            if 'date' in donation:
                if isinstance(donation['date'], datetime):
                    donation_date = donation['date'].strftime('%Y-%m-%d')
                else:
                    donation_date = str(donation['date'])
            elif 'donation_date' in donation:
                if isinstance(donation['donation_date'], datetime):
                    donation_date = donation['donation_date'].strftime('%Y-%m-%d')
                else:
                    donation_date = str(donation['donation_date'])
            elif 'created_at' in donation:
                if isinstance(donation['created_at'], datetime):
                    donation_date = donation['created_at'].strftime('%Y-%m-%d')
                else:
                    donation_date = str(donation['created_at'])
            
            # Build HTML content using standard string concatenation
            content = '<div class="activity-details">'
            content += '<div class="details-item"><span class="details-label">Purpose:</span>'
            content += '<span class="details-value">' + str(donation.get('purpose', donation.get('donation_type_name', 'General Donation'))) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Date:</span>'
            content += '<span class="details-value">' + donation_date + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Amount:</span>'
            content += '<span class="details-value">₹' + str(donation.get('amount', 0)) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Status:</span>'
            content += '<span class="details-value">' + str(donation.get('status', 'N/A')) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Donation ID:</span>'
            content += '<span class="details-value">' + str(donation.get('_id', 'N/A')) + '</span></div>'
            
            content += '<div class="details-item"><span class="details-label">Transaction ID:</span>'
            content += '<span class="details-value">' + str(donation.get('transaction_id', donation.get('payment_id', 'N/A'))) + '</span></div>'
            
            content += '</div>'
            
            return jsonify({"title": title, "content": content})
        
        else:
            return jsonify({"error": "Invalid activity type"}), 400
            
    except Exception as e:
        app.logger.error(f"Error fetching activity details: {str(e)}")
        return jsonify({"error": "Failed to fetch activity details"}), 500

@user_bp.route("/cancel-activity/<type>/<id>", methods=['POST'])
@login_required
def cancel_activity(type, id):
    """Cancel a pending seva or donation"""
    try:
        # Make sure user is in session
        if 'user' not in session:
            return jsonify({"error": "User not authenticated", "success": False}), 401
        
        user_data = session['user']
        user_id = user_data['id']
        
        # Process cancellation based on type
        if type == 'seva':
            # Verify user owns this seva and it's in pending status
            seva = seva_collection.find_one({
                "_id": ObjectId(id), 
                "user_id": user_id,
                "status": "pending"
            })
            
            if not seva:
                return jsonify({
                    "success": False, 
                    "message": "Seva not found, already processed, or you don't have permission to cancel it."
                }), 404
            
            # Update the seva status to cancelled
            result = seva_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {
                    "status": "cancelled",
                    "payment_status": "cancelled",
                    "cancelled_at": datetime.now(),
                    "cancellation_reason": "User cancelled"
                }}
            )
            
            if result.modified_count > 0:
                app.logger.info(f"User {user_id} cancelled seva {id}")
                return jsonify({
                    "success": True,
                    "message": "Seva has been successfully cancelled."
                })
            else:
                app.logger.error(f"Failed to update seva status for cancellation: {id}")
                return jsonify({
                    "success": False,
                    "message": "Failed to cancel seva. Please try again."
                }), 500
                
        elif type == 'donation':
            # Verify user owns this donation and it's in pending status
            donation = donations_collection.find_one({
                "_id": ObjectId(id),
                "$or": [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": user_id}
                ],
                "status": "pending"
            })
            
            if not donation:
                return jsonify({
                    "success": False, 
                    "message": "Donation not found, already processed, or you don't have permission to cancel it."
                }), 404
            
            # Update the donation status to cancelled
            result = donations_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {
                    "status": "cancelled",
                    "payment_status": "cancelled",
                    "cancelled_at": datetime.now(),
                    "cancellation_reason": "User cancelled"
                }}
            )
            
            if result.modified_count > 0:
                app.logger.info(f"User {user_id} cancelled donation {id}")
                return jsonify({
                    "success": True,
                    "message": "Donation has been successfully cancelled."
                })
            else:
                app.logger.error(f"Failed to update donation status for cancellation: {id}")
                return jsonify({
                    "success": False,
                    "message": "Failed to cancel donation. Please try again."
                }), 500
        
        else:
            return jsonify({
                "success": False,
                "message": "Invalid activity type."
            }), 400
            
    except Exception as e:
        app.logger.error(f"Error cancelling activity: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }), 500

@user_bp.route("/email-verify")
def email_verify():
    """Show a form to request verification OTP for unverified accounts"""
    return render_template("user/manual_verify.html")

@user_bp.route("/email-verify", methods=["POST"])
def process_email_verify():
    """Process the email verification request form"""
    email = request.form.get("email")
    
    if not email:
        flash("Email is required", "danger")
        return redirect(url_for("user.email_verify"))
    
    # Find the user in the database
    user = user_collection.find_one({"email": email})
    
    if not user:
        flash("No account found with this email", "danger")
        return redirect(url_for("user.email_verify"))
    
    if user.get("verified", False):
        flash("Your account is already verified. You can log in now.", "info")
        return redirect(url_for("user.login"))
    
    # Generate a new OTP for verification
    otp = ''.join(random.choices('0123456789', k=6))
    expiration_time = time.time() + 600  # 10 minutes in seconds
    
    # Update OTP in database
    user_collection.update_one(
        {"email": email},
        {"$set": {
            "registration_otp": otp,
            "registration_otp_time": expiration_time
        }}
    )
    
    # Store email in session for the next step
    session['email'] = email
    session.modified = True
    
    # Send the OTP email
    try:
        send_registration_otp(email, otp)
        flash("Verification OTP has been sent to your email. Please check your inbox.", "success")
    except Exception as e:
        app.logger.error(f"Failed to send verification OTP: {str(e)}")
        flash("Failed to send verification OTP. Please try again later.", "danger")
        return redirect(url_for("user.email_verify"))
    
    # Redirect to the OTP verification page
    return redirect(url_for("user.verify_registration_otp", email=email))

@user_bp.route("/verify-registration")
def verify_registration_redirect():
    """Helper route to manually reach the OTP verification page"""
    email = request.args.get('email') or session.get('email')
    
    if not email:
        flash('Email not found. Please register or check your email.', 'danger')
        return redirect(url_for('user.register'))
        
    # Check if this email exists and is unverified
    user = user_collection.find_one({"email": email})
    
    if not user:
        flash('No account found with this email.', 'danger')
        return redirect(url_for('user.register'))
        
    if user.get('verified', False):
        flash('Your account is already verified. Please log in.', 'info')
        return redirect(url_for('user.login'))
    
    # Store email in session for the verification process
    session['email'] = email
    session.modified = True
    
    return redirect(url_for('user.verify_registration_otp', email=email))
