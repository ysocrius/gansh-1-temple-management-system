# Temple Management System

*A Complete Solution for Temple Management and Visitor Services*

*Submitted as part of the requirements for Software Engineering Mini Project Lab for 2nd Semester*

## Master of Computer Science

Submitted by 
**Student Name1**                 *Register Number1*
**Student Name2**                 *Register Number2*

Under the guidance of

**Dr. Velmurugan R**

---

## CERTIFICATE

This is to certify that the project titled **Temple Management System** has been successfully completed by Mr. / Ms. **Student Name** with Reg. No. **Ur Reg. No.**, as part of the requirements for Software Engineering Mini Project Lab with course code MCC2P2B21, for the 2nd Semester M.Sc., CS course during the academic year 2024-2026 as set by Bangalore North University.


Faculty In-charge                                                        Head of the Department
        
Valued by                                                        
Examiner 1:_______________________                            Date:        
Examiner 2:_______________________                        Centre: Kristu Jayanti College        

---

## ACKNOWLEDGEMENT

First of all, we want to thank God for blessing us so much. Our faith gave us the strength to work hard on this project.

We want to thank Rev. Fr. Dr. Augustine George, our respected Principal, for helping us all the time. We also thank Rev. Fr. Lijo P Thomas, our Vice-Principal and Chief Finance Officer, for giving us the best facilities to work with.

We are super thankful to Dr. Kumar R, Head of Computer Science (PG) Department, for giving us enough time to work on our project and all the software we needed.

We really want to thank Dr. Velmurugan R, our project guide, for teaching us about project development and helping us finish on time.

We thank all our teachers who helped us finish this project. 

We also thank our friends who pointed out our mistakes and guided us, and everyone else who helped us along the way.

---

## SYNOPSIS

The Temple Management System helps temples work better while keeping their old values. Today's temples face many problems with paper records, limited access, and slow processes that make things hard for both temple workers and visitors.

Our web system makes temple work easier with a digital platform built using Flask and MongoDB. The system lets users sign up safely, make donations online, book services, manage events, and gives tools for managers.

The system makes temple work automatic, helps visitors use services easily, and makes management work smoother. It cuts down on manual work while keeping temple traditions.

**End Users:**
- Temple Managers and Staff
- Visitors and Worshippers
- Event Participants
- Donors and Sponsors
- Religious Service Participants

---

## CONTENTS

1. [Introduction](#1-introduction)
   1.1. [System Definition](#11-system-definition)
   1.2. [Project Description](#12-project-description)
2. [System Study](#2-system-study)
   2.1. [Existing System](#21-existing-system)
   2.2. [Proposed System](#22-proposed-system)
   2.3. [Data Flow Diagram](#23-data-flow-diagram)
   2.4. [ER Diagram](#24-er-diagram)
3. [System Configuration](#3-system-configuration)
   3.1. [Hardware Configuration](#31-hardware-configuration)
   3.2. [Software Configuration](#32-software-configuration)
4. [Details of Software](#4-details-of-software)
   4.1. [Overview of Front End](#41-overview-of-front-end)
   4.2. [Overview of Back End](#42-overview-of-back-end)
5. [System Design](#5-system-design)
   5.1. [Architectural Design](#51-architectural-design)
   5.2. [Input Design](#52-input-design)
   5.3. [Output Design](#53-output-design)
   5.4. [Database Design](#54-database-design)
6. [Source Code](#6-source-code)
7. [Testing](#7-testing)
8. [Implementation](#8-implementation)
9. [Screen Shot](#9-screen-shot)
10. [Conclusion](#10-conclusion)
11. [Bibliography](#11-bibliography)

## 1. Introduction
*This section presents an overview of the Temple Management System, outlining its purpose and scope.*

### 1.1. System Definition

The Temple Management System is a website that helps temples do their daily work better. It takes care of all the office work and day-to-day tasks of a temple. This system fixes many problems in how temples are run by making one place where both temple workers and visitors can do what they need. It has many parts like user accounts, collecting donations, booking services (sevas), planning events, and getting feedback from visitors.

Temples need many special things like handling visitor sign-ups, taking donations, setting up religious services, planning events, and keeping track of money. Our system turns all these paper tasks into computer tasks. This saves time, makes fewer mistakes, and makes things easier for everyone.

The system uses new web tools and works like a client-server system. It has a nice front-end that works on all devices and a strong back-end that keeps data safe. By using Flask and MongoDB, our system can grow bigger and change to fit what any temple needs.

### 1.2. Project Description
*This section describes the modules and functional components of the Temple Management System.*

#### 1.2.1. Project Modules

The Temple Management System has these main parts:

* **User Management Module**
  - Sign up with email checking
  - Login with password
  - Google login to make it easy
  - Reset password with code sent to your phone
  - Profile settings where you can change your info

* **Donation Management Module**
  - Give money online through Razorpay
  - Different ways to pay (cards, UPI, netbanking)
  - PDF receipts to show you gave money
  - Option to give without showing your name
  - Simple tracking of donations

* **Service (Seva) Management Module**
  - Look at different types of sevas
  - Book sevas by picking a date
  - Pay through Razorpay
  - Get a booking confirmation
  - Get a simple receipt

* **Event Management Module**
  - See coming temple events
  - Simple event calendar
  - Basic event information
  - Look at past temple events

* **Testimonial Module**
  - Share what you think about the temple
  - Give stars for rating
  - Temple staff can check before showing to others
  - See what other people said about the temple

* **Administration Module**
  - Simple screen for temple staff
  - Basic user handling
  - Approve what people say about the temple
  - See donation and seva records

#### 1.2.2. Reports Generated

The system gives basic information about:

* **Donation Information**
  - List of recent donations
  - Simple donation summaries
  - Track if payment was done

* **Service Information**
  - List of seva bookings
  - Seva booking status

* **Event Information**
  - List of upcoming and past events
  - Basic event details

* **User Information**
  - Basic user listing
  - User verification status

## 2. System Study
*This section looks at old temple management ways and presents our new computer solution.*

### 2.1. Existing System
*Current temple management approaches and their problems*

Most temples still use old paper methods that have been used for many years. Sharma & Kumar [1] say that this old system has many problems today:

#### 2.1.1. Manual Record Keeping

Temples usually keep paper books for everything:
- People's details and member lists
- Donation books and paper receipts
- Service (seva) planning notebooks
- Event calendars and attendance papers
- Money books and account records

This paper system needs lots of work, mistakes happen often, and it's too slow when there are many people and donations [3].

#### 2.1.2. In-Person Processes

In old temple systems, people have to visit the temple in person for almost everything:
- They have to give donations in person using cash or checks
- They must talk face-to-face with temple staff to book services
- Event sign-ups happen only at the temple
- Getting receipts means another trip to the temple

This need to come in person is a problem for people who live far away or can't travel easily [1].

#### 2.1.3. Limited Communication Channels

In old temple systems, news travels through:
- Notice boards inside the temple
- Printed newsletters
- People telling each other
- Sometimes phone calls for important things

These few ways of sharing news cause delays and less community involvement [10].

#### 2.1.4. Financial Management Challenges

The old way of handling money has many problems:
- Counting donations and expenses by hand
- Keeping cash donations safe
- Hand-written receipts that might have mistakes
- Hard to make money reports
- Few payment options, mostly cash

Research by Singh & Patel [11] shows that digital systems greatly improve financial tracking accuracy.

#### 2.1.5. Limitations of the Existing System

The old temple management system has these big problems:

1. **Takes Too Much Time**: Paper tasks take too much time and work.
2. **Mistakes Happen**: Hand-written records often have errors.
3. **Limited Time Access**: Services are only available when the temple is open.
4. **Can't Grow Easily**: Paper systems can't handle more people and donations.
5. **No Data Study**: Hard to look at data to make services better.
6. **Safety Risks**: Paper records and cash handling aren't very safe.
7. **Limited Reach**: Can't help people who can't visit the temple.
8. **Storage Problems**: Keeping all those papers needs a lot of space.

These problems show why we need a modern, computer solution that fixes these issues while respecting temple traditions [1, 10, 12].

### 2.2. Proposed System
*Our computer solution for temple management problems*

Our Temple Management System will fix the problems of the old paper system by using new computer tools to make an easy-to-use website for all temple work.

#### 2.2.1. System Overview

The Temple Management System is a website that puts together all parts of temple work. It joins old temple ways with new computer ease, with tools that make office work easier and make visitors happier.

#### 2.2.2. Key Features of the Proposed System

**1. User Management Module**
- Safe sign-up and login
- Your own profile with your details
- Different powers for visitors, staff, and temple head
- Help if you forget your password

**2. Donation Management Module**
- Give money online with many payment ways
- Get receipts right away
- See how much you have given before
- Many types of donations you can make

**3. Service (Seva) Booking Module**
- See all sevas you can book with details
- Book online and pick date and time
- Pay online for sevas
- Get a message that your booking is done

**4. Event Management Module**
- Make and share temple events
- Keep track of who is coming
- Calendar to see all events
- Handle things needed for events
- Send messages to remind people

**5. Testimonial System Module**
- Tell others about your temple visit
- Temple staff check before showing to all
- See what other visitors said
- Give stars and say what you liked

**6. Administration Module**
- Screen showing important numbers
- Handle users and what they can do
- See money reports and check them
- Change how the system works
- Save data so nothing gets lost

#### 2.2.3. Good Things About the New System

Our Temple Management System has many good points compared to the old way:

1. **Work Gets Done Faster**: Computer does the boring parts and makes work smoother.
2. **Less Wrong Information**: Computer records have fewer mistakes in typing and money math.
3. **Use Any Time**: Online site lets visitors use services day or night, any day.
4. **Helps More People**: Good for visitors who can't come to the temple in person.
5. **Clear Money Tracking**: See exactly where donations go and what was spent.
6. **Better News Sharing**: Computer sends notices to keep visitors informed.
7. **Information Stays Safe**: Good protection for personal and money details.
8. **Learn What Works**: Collected information helps make services better.
9. **Saves Money**: Need less paper, printing, and space for storing papers.
10. **Can Get Bigger**: System works fine even when more people use it.

#### 2.2.4. Who Gets What Benefits

**For Temple Workers:**
- Less office work because computer does it
- Full reports to see what's happening
- Better way to handle money and track it
- Better way to talk with visitors
- Easier planning for events and sevas

**For Temple Visitors:**
- Easy to use temple services
- Many ways to give donations
- Get receipts right away
- Your own screen with your history and upcoming bookings
- Better news about temple happenings

#### 2.2.5. How We Will Build It

We'll build the Temple Management System step by step:

1. **Step 1**: Basic user accounts and donation giving
2. **Step 2**: Seva booking and event planning
3. **Step 3**: Visitor comments and reports
4. **Step 4**: Make it work well on phones and add more features

This step-by-step way lets us add slowly, get visitor opinions, and make the system better at each stage.

### 2.3. Data Flow Diagram
*Visual representation of information flow through the system*

The Data Flow Diagram (DFD) shows how information moves through the Temple Management System, between different processes, outside users, and data storage.

#### 2.3.1. Level 0 DFD (Context Diagram)

**Figure 2.1: Temple Management System Context Diagram**

[Place for Temple Management System Context Diagram]

#### 2.3.2. Level 1 DFD (Major Processes)

**Figure 2.2: Temple Management System Level 1 DFD**

[Place for Temple Management System Level 1 DFD]

#### 2.3.3. Level 2 DFD (Detailed Processes)

**Figure 2.3: Temple Management System Level 2 DFD - User Management**

[Place for Temple Management System User Management DFD]

**Figure 2.4: Temple Management System Level 2 DFD - Donation Management**

[Place for Temple Management System Donation Management DFD]

**Figure 2.5: Temple Management System Level 2 DFD - Seva Management**

[Place for Temple Management System Seva Management DFD]

#### 2.3.4. Level 3 DFD (Process Details)

Level 3 DFDs provide the most detailed view of specific processes within the system.

**Figure 2.6: Temple Management System Level 3 DFD - User Authentication Process**

[Place for Temple Management System User Authentication Process DFD]

This diagram shows the detailed data flow for user authentication, including:
- Login credential validation
- Session creation
- Authentication failure handling
- Password recovery flow
- Account lockout procedures

**Figure 2.7: Temple Management System Level 3 DFD - Payment Processing**

[Place for Temple Management System Payment Processing DFD]

This diagram details the payment processing flow, including:
- Payment information collection
- Payment gateway interaction
- Transaction verification
- Receipt generation
- Error handling procedures

**Figure 2.8: Temple Management System Level 3 DFD - Notification System**

[Place for Temple Management System Notification System DFD]

This diagram shows the notification system's detailed data flow:
- Event triggering
- Notification template selection
- Delivery method determination
- Notification status tracking
- Delivery confirmation

### 2.4. ER Diagram
*Database structure and relationships between entities*

**Figure 2.9: Temple Management System ER Diagram**

[Place for Temple Management System ER Diagram]

Key entities in the ER diagram include:

1. **User**: Represents devotees, staff, and administrators with attributes like username, password, contact information, etc.

2. **Donation**: Records donation transactions with amount, date, purpose, etc.

3. **Receipt**: Stores receipt information associated with donations.

4. **Seva Booking**: Contains details of service bookings including service type, date, time, etc.

5. **Event**: Holds information about temple events including title, description, date, venue, etc.

6. **Payment**: Records payment transactions across donations, services, and event registrations.

7. **Testimonial**: Stores user testimonials with content, approval status, etc.

8. **Category**: Represents categories for both donations and services.

9. **Registration**: Contains event registration information.

The relationships between these entities capture the essential data associations in the system, enabling comprehensive data management and retrieval. Each entity contains appropriate attributes that store specific pieces of information, and the connections between entities establish the logical structure of the database.

## 3. System Configuration
*Hardware and software requirements for development and deployment*

### 3.1. Hardware Configuration
*Hardware specifications needed for system development and deployment*

#### 3.1.1. Development Environment

We built the Temple Management System using these computer specs:

| Part | Details |
|-----------|---------------|
| Processor | Intel Core i7 (8th Gen) or similar |
| RAM | 16 GB DDR4 |
| Storage | 512 GB SSD |
| Display | 1920 x 1080 screen |
| Network | Fast Ethernet and Wi-Fi 5 (802.11ac) |
| Input Devices | Standard keyboard and mouse |

#### 3.1.2. Minimum Deployment Requirements

For the system to work well in real use, you need at least:

**Server Requirements:**
| Component | Specification |
|-----------|---------------|
| Processor | Intel Xeon E5 or similar (4+ cores) |
| RAM | 8 GB (minimum), 16 GB (recommended) |
| Storage | 100 GB SSD (minimum) |
| Network | Gigabit Ethernet connection |
| Backup | External storage for database backups |

**Client Requirements:**
| Component | Specification |
|-----------|---------------|
| Processor | Any modern processor (2+ cores) |
| RAM | 4 GB (minimum) |
| Browser | Chrome 80+, Firefox 75+, Safari 13+, Edge 80+ |
| Display | 1366 x 768 resolution (minimum) |
| Network | Broadband internet connection (1 Mbps+) |

#### 3.1.3. Mobile Device Compatibility

The system works on standard mobile devices with modern browsers.

### 3.2. Software Configuration
*Software tools and technologies used in the system*

#### 3.2.1. Development Tools and Environment

We used these software tools to build the system:

**Development Environment:**
| Tool | Version | Purpose |
|------|---------|---------|
| Visual Studio Code | 1.60+ | Main code editor |
| Git | 2.30+ | Version control system |
| GitHub | N/A | Repository hosting |
| Python | 3.8+ | Main programming language |
| pip | 21.0+ | Python package manager |
| Virtual Environment | venv | Dependency isolation |

**Development Operating Systems:**
- Windows 10/11
- macOS 11+ (Big Sur or later)
- Ubuntu 20.04 LTS

#### 3.2.2. Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Main programming language |
| Flask | 2.0+ | Web framework |
| MongoDB | 5.0+ | NoSQL database |
| Flask-Session | 0.4+ | Session management |
| Flask-Mail | 0.9+ | Email sending |
| Flask-WTF | 1.0+ | Form handling and security |
| PyMongo | 4.0+ | MongoDB connector for Python |
| Werkzeug | 2.0+ | WSGI utility library |
| Razorpay SDK | 1.3+ | Payment gateway integration |
| Authlib | 1.0+ | Google OAuth login |
| bcrypt | 4.0+ | Password hashing |
| itsdangerous | 2.1+ | Token generation |
| ReportLab | 3.6+ | PDF generation for receipts |
| Requests | 2.27+ | HTTP requests |

#### 3.2.3. Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| HTML5 | Latest standard | Markup language |
| CSS3 | Latest standard | Styling |
| JavaScript | ES6+ | Client-side scripting |
| jQuery | 3.6+ | JavaScript library |
| Bootstrap | 5.0+ | CSS framework |
| Jinja2 | 3.0+ | Templating engine |
| AJAX | N/A | Asynchronous requests |

#### 3.2.4. Database Configuration

| Component | Specification |
|-----------|---------------|
| Database System | MongoDB |
| Version | 5.0+ |
| Authentication | Username/Password |
| Connection | PyMongo driver |
| Storage | MongoDB Atlas cloud database |
| Deployment | Cloud-based deployment |

#### 3.2.5. Deployment Environment

| Component | Specification |
|-----------|---------------|
| Hosting Service | Render.com |
| Server Type | Web Service |
| Environment | Production |
| Database | MongoDB Atlas |
| Domain | gansh-1-temple-management-system.onrender.com |

#### 3.2.6. External Services

| Service | Purpose |
|---------|---------|
| Razorpay | Payment processing |
| SMTP Service | Email delivery |
| Google Maps API | Location services for events |
| Cloud Storage | Media and backup storage |

## 4. Details of Software
*Front-end and back-end components of the Temple Management System*

### 4.1. Overview of Front End
*User interface components and design principles*

The front-end of our Temple Management System uses modern web technologies to create a nice-looking and easy-to-use interface. We used HTML5, CSS3, JavaScript, and Bootstrap to make sure the website looks good on all devices, from computers to mobile phones.

#### 4.1.1. Template System


Our system uses Jinja2 templates organized like this:

1. **Base Templates**:
   - `base.html`: Main template with common parts (header, footer, navigation)
   - `admin_base.html`: Base template for admin screens
   - `error_base.html`: Template for error pages

2. **User Interface Templates**:
   - `user/`: Folder with templates for users
     - `index.html`: Home page with hero section and announcements
     - `login.html`: Login page with email and password fields
     - `register.html`: Registration form with OTP verification
     - `dashboard.html`: User dashboard showing recent activities
     - `profile.html`: User profile with editable information
     - `donations.html`: Donation page with payment options
     - `user_seva.html`: Seva booking page with filtering options
     - `events.html`: Event listing page with calendar view
     - `verify_registration_otp.html`: OTP verification for new accounts
     - `reset_password.html`: Password recovery interface
     - `forgot_password.html`: Interface to request password reset
     - `temple_history.html`: Page displaying temple history
     - `contact.html`: Contact information and form
     - `gallery.html`: Image gallery of temple and events

3. **Admin Interface Templates**:
   - `admin/`: Folder with templates for admins
     - `admin_dashboard.html`: Admin dashboard with system statistics
     - `manage_users.html`: User management interface
     - `manage_events.html`: Event management interface
     - `admin_seva_table.html`: Seva management dashboard
     - `admin_donation_list.html`: Donation management interface
     - `manage_testimonials.html`: Testimonial moderation interface
     - `manage_donation_goals.html`: Manage donation campaigns
     - `sidebar.html`: Admin navigation sidebar component

4. **Component Templates**:
   - `components/`: Folder for reusable parts
     - `navigation.html`: Navigation bar
     - `sidebar.html`: Sidebar menu
     - `forms/`: Form components
     - `cards/`: Card layouts
     - `tables/`: Table layouts

5. **Email Templates**:
   - `email/`: Folder for email templates
     - `confirmation.html`: Account confirmation email
     - `reset_password.html`: Password reset email
     - `donation_receipt.html`: Donation receipt email
     - `seva_booking.html`: Seva booking confirmation
     - `event_reminder.html`: Event reminder email

6. **Error Templates**:
   - `errors/`: Folder for error pages
     - `404.html`: Page not found error
     - `500.html`: Server error page
     - `403.html`: Access denied page

#### 4.1.2. Template Features

Following is the source code for the Temple Management System's user interface design:

1. **Navigation System**:
   - Menu bar that changes size for different screens
   - Sidebar navigation for admin pages
   - Breadcrumb trails to show where you are
   - Menus that change based on who you are

2. **Responsive Design**:
   - Layouts that adjust to screen size
   - Mobile-first approach so it works well on phones
   - Flexible grid systems for content
   - Special rules to optimize display for different screens

3. **Interactive Elements**:
   - Forms with real-time checking
   - Pop-up dialogs for confirmations
   - Dropdown menus to save space
   - Accordions and tabs for organizing information
   - Tables you can sort and filter

4. **Visual Feedback**:
   - Loading indicators when something is happening
   - Toast notifications for messages
   - Status indicators (success, error, warning)
   - Progress trackers for multi-step processes

These template features demonstrate the responsive, user-friendly design of the Temple Management System, with dedicated interfaces for visitors, devotees, and administrators. The use of modern web design techniques ensures the system is accessible across different devices while maintaining a consistent aesthetic that reflects the traditional temple environment in a digital context.

### 4.2. Overview of Back End
*Server-side components and functionality*

The back-end of our system does all the important work behind the scenes. It's built using Flask and MongoDB, and it's organized in a way that makes it easy to maintain, expand, and keep secure.

#### 4.2.1. Technologies Used

**Core Technologies:**
- **Python 3.8+**: Main programming language
- **Flask 2.0+**: Web framework for handling requests
- **MongoDB 5.0+**: Database for storing data
- **PyMongo 4.0+**: Python connector for MongoDB

**Extensions and Libraries:**
- **Flask-Session**: Manages user sessions
- **Flask-Mail**: Handles email sending
- **Flask-WTF**: Handles forms and security
- **Werkzeug**: Toolkit for web applications
- **Pillow**: Processes images for profiles
- **PyJWT**: Handles secure tokens for authentication
- **passlib**: Handles password security

**External Services Integration:**
- **Razorpay SDK**: Payment gateway integration
- **SMTP Libraries**: Email delivery services

#### 4.2.2. Back-End Architecture

The Temple Management System follows a modular pattern that organizes code by function:

1. **Application Factory**: Handles app setup and startup
   - Environment settings
   - Extension setup
   - Blueprint setup
   - Error handling setup

2. **Blueprints**: Organized routes by feature
   - User management blueprint
   - Donation processing blueprint
   - Service (seva) booking blueprint
   - Event management blueprint
   - Testimonial system blueprint
   - Admin blueprint

3. **Service Layer**: Handles business rules
   - User login and permissions
   - Donation processing workflow
   - Service booking checking and confirmation
   - Event management and sign-up
   - Report creation and data review

4. **Data Access Layer**: Handles database work
   - MongoDB collection access methods
   - Query building and running
   - Data checking and change
   - Indexing for speed

5. **Utility Modules**: Shared functions
   - Email template creation and sending
   - PDF creation for receipts
   - Date and time handling
   - Logging and watching

#### 4.2.3. Database Design

The MongoDB database is built around collections that show the main things in the system:

**Main Collections:**
- **users**: Visitor and manager accounts
- **donations**: Donation records
- **receipts**: Donation receipt information
- **sevas**: Available service types
- **seva_bookings**: Service booking records
- **events**: Temple event information
- **event_registrations**: Event sign-up records
- **testimonials**: User feedback
- **categories**: Types for donations and services
- **settings**: System setup details

**Database Operations:**
- CRUD operations for all items
- Data grouping for reports
- Text search
- Location-based features

#### 4.2.4. API Structure

The Temple Management System uses a RESTful API for communication between front-end and back-end parts:

**API Endpoints by Area:**
- **/api/auth**: Login and user management
- **/api/donations**: Donation handling and management
- **/api/sevas**: Service booking and checking
- **/api/events**: Event information and sign-up
- **/api/testimonials**: Feedback sending and getting
- **/api/admin**: Manager functions and reporting

**API Response Format:**
- JSON structure for data sharing
- Standard success/error response patterns
- HTTP status codes for result showing
- Paging for big data sets

#### 4.2.5. Security Implementation

The back-end uses several safety measures to protect user data and system health:

1. **Login and Permissions**:
   - Secure password hiding with bcrypt
   - Role-based access control
   - Session management with secure cookies
   - CSRF protection for all state-changing actions

2. **Data Protection**:
   - Input checking and cleaning
   - Safe queries to prevent hacking
   - Output coding to prevent XSS
   - Data access controls based on user roles

3. **Payment Security**:
   - Link with secure payment gateway
   - Payment checking and validation
   - Safe handling of payment information
   - Logs for money actions

4. **System Security**:
   - HTTPS/TLS encryption for all communications
   - Rate limits to prevent misuse
   - IP filtering for manager access
   - Regular safety updates

#### 4.2.6. Database Queries and Operations
*Example queries used in the system*

Following is the source code for the Temple Management System's database operations:

The Temple Management System employs various MongoDB queries and operations for efficient data management:

**Common Query Patterns:**

##### 4.2.6.1. User Authentication
```python
user = user_collection.find_one({
    "email": email,
    "verified": True
})

# Password verification
if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
    # Login successful
    session["user"] = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }
    # Update last login time
    user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.now()}}
    )
```

##### 4.2.6.2. User Registration with OTP Verification
```python
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

# Verify OTP and complete registration
user = user_collection.find_one({
    "email": email,
    "registration_otp": otp,
    "registration_otp_time": {"$gte": time.time()}
})
if user:
    # Mark user as verified
    user_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"verified": True},
            "$unset": {"registration_otp": "", "registration_otp_time": ""}
        }
    )
```

##### 4.2.6.3. Google OAuth Integration
```python
# Check if user exists with this email
user = user_collection.find_one({"email": user_info['email']})

if user:
    # Update existing user's Google profile data
    user_collection.update_one(
        {"_id": user['_id']},
        {
            "$set": {
                "google_id": user_info['id'],
                "google_profile_data": user_info,
                "verified": True,  # Google accounts are pre-verified
                "auth_method": "google",
                "last_login": datetime.now()
            }
        }
    )
else:
    # Create a new user with Google data
    new_user = {
        "name": user_info.get('name', ''),
        "email": user_info['email'],
        "verified": True,
        "google_id": user_info['id'],
        "google_profile_data": user_info,
        "auth_method": "google",
        "created_at": datetime.now(),
        "last_login": datetime.now()
    }
    
    result = user_collection.insert_one(new_user)
```

##### 4.2.6.4. Donation Creation with Razorpay Integration
```python
# Create Razorpay order
client = razorpay.Client(auth=(key_id, key_secret))
order_data = {
    'amount': amount_in_paise,
    'currency': 'INR',
    'receipt': f'don_{int(time.time())}',
    'notes': {
        'donation_type': donation_type,
        'user_id': user_id
    }
}
order = client.order.create(order_data)

# Store donation after successful payment
donation_data = {
    'transaction_id': transaction_id,
    'user_id': user_id,
    'donation_type': donation_type_id,
    'donation_type_name': donation_type_name,
    'amount': float(amount),
    'payment_id': razorpay_payment_id,
    'order_id': razorpay_order_id,
    'donor_name': donor_name,
    'email': email,
    'phone': phone,
    'is_anonymous': is_anonymous,
    'date': datetime.now(),
    'status': 'completed'
}
result = donations_collection.insert_one(donation_data)
```

##### 4.2.6.5. Seva (Service) Booking Process
```python
# Check if seva is available on selected day
day_name = selected_date.strftime('%A')
if day_name not in seva['available_days']:
    flash(f'Seva is not available on {day_name}', 'danger')
    return redirect(url_for('seva.details', seva_id=seva_id))

# Check participant limit
if participants > seva['max_participants']:
    flash(f'Maximum {seva["max_participants"]} participants allowed', 'danger')
    return redirect(url_for('seva.details', seva_id=seva_id))

# Check availability (existing bookings)
existing_booking = seva_collection.find_one({
    'seva_id': ObjectId(seva_id),
    'scheduled_date': selected_date,
    'scheduled_time': time_slot,
    'status': {'$in': ['pending', 'confirmed']}
})

# Create booking
booking_id = seva_collection.insert_one({
    'booking_reference': booking_ref,
    'user_id': ObjectId(user_id),
    'seva_id': ObjectId(seva_id),
    'scheduled_date': selected_date,
    'scheduled_time': time_slot,
    'participants': participants,
    'special_requests': special_requests,
    'amount': seva['price'],
    'status': 'pending',
    'created_at': datetime.now()
}).inserted_id
```

##### 4.2.6.6. Event Management Operations
```python
# Add new event
event_data = {
    "title": title,
    "venue": venue,
    "date": date,
    "description": description,
    "created_at": datetime.now()
}
result = events_collection.insert_one(event_data)

# Fetch upcoming events
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
upcoming_events = list(events_collection.find({"date": {"$gte": today}}).sort("date", 1))

# Fetch past events
seven_days_ago = datetime(today.year, today.month, today.day - 7)
past_events = list(events_collection.find({
    "date": {
        "$lt": today,
        "$gte": seven_days_ago
    }
}).sort("date", -1))
```

##### 4.2.6.7. Testimonial System
```python
# Submit testimonial
testimonial_data = {
    'user_id': ObjectId(user_id),
    'user_name': user_name,
    'message': message,
    'rating': rating,
    'date_submitted': datetime.utcnow(),
    'status': 'pending'  # pending, approved, rejected
}
db.testimonials.insert_one(testimonial_data)

# Approve testimonial
result = db.testimonials.update_one(
    {"_id": ObjectId(testimonial_id)},
    {"$set": {
        "status": "approved",
        "reviewed_by": ObjectId(admin_id),
        "reviewed_at": datetime.now()
    }}
)

# Display approved testimonials
testimonials_cursor = db.testimonials.find({"status": "approved"}).sort("date_submitted", -1).limit(3)
```

##### 4.2.6.8. Admin Dashboard Statistics
```python
# Get statistics from collections
stats = {
    "events": {
        "total": events_collection.count_documents({}),
        "upcoming": events_collection.count_documents({"date": {"$gte": datetime.now()}}),
        "recent_events": list(events_collection.find().sort("date", -1).limit(5))
    },
    "sevas": {
        "total_types": seva_list.count_documents({}),
        "total_bookings": seva_collection.count_documents({}),
        "recent_bookings": list(seva_collection.find().sort("_id", -1).limit(5))
    },
    "donations": {
        "total_types": donations_list.count_documents({}),
        "total_donations": donations_collection.count_documents({}),
        "recent_donations": list(donations_collection.find().sort("_id", -1).limit(5)),
        "total_amount": sum(float(donation.get("amount", 0)) for donation in donations_collection.find())
    },
    "users": {
        "total": user_collection.count_documents({}),
        "verified": user_collection.count_documents({"verified": True})
    }
}
```

##### 4.2.6.9. Password Reset with OTP
```python
# Generate OTP for password reset
otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
# Save OTP in database with expiration
user_collection.update_one(
    {"email": email},
    {"$set": {
        "reset_otp": otp,
        "reset_otp_expiry": datetime.now() + timedelta(minutes=15)
    }}
)

# Verify OTP
user = user_collection.find_one({
    "email": email,
    "reset_otp": otp,
    "reset_otp_expiry": {"$gt": datetime.now()}
})

# Update password after verification
hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
user_collection.update_one(
    {"_id": user["_id"]},
    {
        "$set": {"password": hashed_password},
        "$unset": {"reset_otp": "", "reset_otp_expiry": ""}
    }
)
```

##### 4.2.6.10. MongoDB Atlas Connection
```python
import os
from pymongo import MongoClient

# Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://username:password@cluster0.example.mongodb.net/temple_system?retryWrites=true&w=majority")
client = MongoClient(mongo_uri)
db = client["temple_system"]

# Get all the collections we need
user_collection = db["user_collection"]
donations_collection = db["donations_collection"]
seva_collection = db["seva_bookings"]
seva_list = db["seva_list"]
events_collection = db["events_collection"]
donations_list = db["donations_list"]
```

These database operations show how good MongoDB is for handling all the different information needs of the Temple Management System. It also shows how our system works with other services like Razorpay and Google login to give more features.

#### 4.2.7. Utility Modules
*Helper tools that make the system work better*

Following is the source code for the helper tools that make our Temple Management System work better:

The system has several helper tools that do common jobs needed in many places. These tools help with checking if users can log in, connecting to the database, and sending emails.

##### 4.2.7.1. Login Checker Tools
```python
# From utils/decorators.py
from functools import wraps
from flask import g, request, session, redirect, url_for, flash

def with_navigation(f):
    """
    Decorator to ensure navigation state is tracked properly.
    This sets the current_path in the Flask g object for templates to use.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_path = request.path
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            response = redirect(url_for('user.login'))
            # Add cache control headers
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
            
        if not session['user'].get('is_admin', False):
            flash('You do not have permission to access this page.', 'danger')
            response = redirect(url_for('general.home'))
            # Add cache control headers
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
            
        # Mark session as modified to ensure it stays active
        session.modified = True
        return f(*args, **kwargs)
    return decorated_function
```

##### 4.2.7.2. Database Connection Tool
```python
# From utils/db.py
from flask import g
from pymongo import MongoClient
from config import Config

def get_db():
    if 'db' not in g:
        client = MongoClient(Config.MONGO_URI)
        g.db = client[Config.MONGO_DB_NAME]
    return g.db
```

##### 4.2.7.3. Email Sending Tool
```python
# From utils/mail.py
from flask_mail import Mail

mail = Mail()

def init_mail(app):
    mail.init_app(app)
```

These helper tools do important jobs in our system:
- **Security Tools**: The login checker tools make sure only the right people can see certain pages. The `with_navigation` tool keeps track of which page you're on, `login_required` checks if you're logged in, and `admin_required` checks if you're a temple manager.
- **Database Tool**: This tool helps all parts of the system connect to MongoDB in the same way. It makes sure we always connect in a good way.
- **Email Tool**: This tool sets up the email system so we can send verification emails, receipts, and notices to users.

These tools help make our code cleaner and easier to fix if there are problems. By putting these common jobs in one place, we don't have to write the same code many times and everything works the same way throughout the system.