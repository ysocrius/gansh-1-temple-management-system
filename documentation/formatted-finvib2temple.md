# PROJECT REPORT ON Temple Management System

*Submitted in partial fulfillment of the requirements for Software Engineering Mini Project Lab for 2nd Semester Master of Computer Science*

## Submitted by

[Your Name] [Your ID]  
[Partner Name] [Partner ID]

## Under the guidance of

[Instructor Name]

# CERTIFICATE

This is to certify that the project titled Temple Management System has been satisfactorily completed by [Your Name] with Reg. No. [Your ID] in partial fulfillment of the requirements for Software Engineering Mini Project Lab with course code MCC2P2B21, for the 2nd Semester Master of Computer Applications course during the academic year 2024-2025 as prescribed by Bangalore North University.

Faculty In-charge                            Head of the Department

Valued by

Examiner 1:                                  Centre: Kristu Jayanti College  
Examiner 2:                                  Date:

# ACKNOWLEDGEMENT

First of all, we would like to thank the God Almighty for all the blessings he has showered on us. Our spiritual quotient gave us more strength and motivation that helped immensely.

We would like to thank Rev. Fr. Dr. Augustine George, our esteemed Principal, for providing us their constant guidance and support. I would also like to thank Rev. Fr. Lijo P Thomas, our Vice-Principal and Chief Finance Officer, for providing us with the best facilities.

We are extremely thankful to our Dr. Kumar R, Head, Department of Computer Science (PG) for giving us the essential support in the form of allocating comfortable project hours and necessary software resources.

We would like to extend our heartfelt thanks to [Instructor Name], our project guide for providing us the necessary details related to project development and process identification enabling us to finish the project within the stipulated time.

We thank all other faculty members who helped us a lot in completing this project.

We thank our class mates, who have pointed out errors and guided us a lot and we thank each and every one who has helped us.

# Synopsis

## Overview
Temple Management System is a modern temple management system designed to help temples manage their daily operations, donations, events, and seva bookings. The system makes it easy for temple administrators to keep track of temple activities and for devotees to book sevas, make donations, and stay updated about temple events.

## Target Audience
Temple Management System is designed for temple administrators who need a simple way to manage temple operations, and for devotees who want to book sevas, make donations, and stay connected with temple activities. It is also useful for temple committees and volunteers who help with temple management.

## Core Features

1. **User Management**:
   - Devotees can register and log in to their accounts
   - Users can update their profile information
   - Secure password reset and email verification

2. **Seva Booking**:
   - Devotees can book various types of sevas online
   - View seva details and history
   - Receive confirmation emails for bookings

3. **Donation Management**:
   - Accept online donations for different purposes
   - Track donation history and generate receipts
   - Set donation goals and track progress

4. **Event Management**:
   - Create and manage temple events
   - Send notifications about upcoming events
   - Allow users to register for events

5. **Admin Dashboard**:
   - Temple administrators can manage all temple activities
   - View reports and analytics
   - Manage user accounts and permissions

6. **Security**:
   - Secure user authentication and authorization
   - Data encryption for sensitive information
   - Regular backups to prevent data loss

7. **User-Friendly Interface**:
   - Clean and modern UI built using HTML, CSS, and JavaScript
   - Responsive design that works on mobile and desktop devices
   - Easy navigation for all users

## END USERS
The end users of Temple Management System include temple administrators who manage the temple's daily operations, devotees who book sevas and make donations, temple committee members who oversee temple activities, and volunteers who help with temple management. The system is designed to be user-friendly for people of all technical backgrounds, making it accessible to both tech-savvy users and those who are less familiar with digital tools.

# CONTENTS

| SI. No. | Particulars | Pg. No |
|---------|-------------|--------|
| 1. | Introduction<br>1.1 System Definition<br>1.2 Project Description | 1 - 2 |
| 2. | System Study<br>2.1 Existing System<br>2.2 Proposed System<br>2.3 Data Flow Diagram<br>2.4 ER Diagram | 3 - 8 |
| 3. | System Configuration<br>3.1 Hardware Configuration<br>3.2 Software Configuration | 9 - 12 |
| 4. | Details of Software<br>4.1 Overview of Front End<br>4.2 Overview of Back End | 13 - 14 |
| 5. | System Design<br>5.1 Architectural Design<br>5.2 Input Design<br>5.3 Output Design<br>5.4 Database Design | 15 - 22 |
| 6. | Source Code | 23 - 45 |
| 7. | Testing | 46 - 50 |
| 8. | Implementation | 51 - 56 |
| 9. | Screen Shot | 57 - 62 |
| 10. | Conclusion | 63 - 65 |
| 11. | Bibliography | 66 - 67 |

# 1. INTRODUCTION

Temple management has become more important in today's digital world. Temples need better ways to handle their daily tasks, donations, events, and seva bookings. Many temples still use old paper-based methods or simple spreadsheets, which can lead to mistakes, wasted time, and poor record-keeping. Temple Management System is designed to solve these problems by providing a complete temple management system that helps temples run smoothly and makes it easier for devotees to connect with temples.

The system uses Flask for the backend and modern web technologies for the frontend, making it secure, easy to use, and able to grow as needed. With features like online seva booking, donation tracking, event management, and admin tools, Temple Management System helps temples work better and gives devotees a better experience.

## 1.1 System Definition

Current temple management systems often have these problems:

- Paper-based records make it hard to find information quickly and can lead to lost data.
- Manual seva booking is time-consuming and can cause scheduling conflicts.
- Tracking donations is difficult without proper digital tools.
- Temple events are not well-promoted to devotees.
- Temple administrators lack good tools to manage temple activities.
- Devotees have trouble booking sevas or making donations when they can't visit the temple.
- There's no easy way to send updates about temple activities to devotees.

## 1.2 Project Description

Temple Management System is a modern temple management system that helps temples run better and makes it easier for devotees to connect with temples. The system offers:

- User Management – Devotees can create accounts, log in, and manage their profiles.
- Seva Booking – Devotees can book sevas online, view their booking history, and get email confirmations.
- Donation Management – Temples can accept online donations, track donation history, and generate receipts.
- Event Management – Temples can create and manage events, and devotees can register for events.
- Admin Dashboard – Temple administrators can manage all temple activities from one place.
- Security – The system uses secure authentication and data encryption to protect sensitive information.
- User-Friendly Interface – The system is easy to use on both mobile and desktop devices.

### MODULES

The following modules are included in Temple Management System:

1. **User Authentication Module**: Handles user registration, login, and security (like password reset and email verification). It ensures secure access to the system.

2. **Seva Management Module**: Lets devotees book sevas online, view seva details, and get confirmation emails. It also helps temple administrators manage seva schedules.

3. **Donation Management Module**: Accepts online donations for different purposes, tracks donation history, and generates receipts. It also helps set donation goals and track progress.

4. **Event Management Module**: Helps temples create and manage events, send notifications about upcoming events, and lets devotees register for events.

5. **Admin Dashboard Module**: Gives temple administrators tools to manage all temple activities, view reports, and manage user accounts.

6. **Notification Module**: Sends emails and alerts to users about seva bookings, donations, events, and other important updates.

7. **Report Generation Module**: Creates reports on donations, seva bookings, and other temple activities to help with planning and decision-making.

# 2. SYSTEM STUDY

Temple Management System combines temple management features (like seva booking, donation tracking, and event management) with tools to help temples run better. It lets temple administrators manage all temple activities from one place and gives devotees an easy way to book sevas, make donations, and stay connected with temple events. The system uses MongoDB to store data securely and Flask to handle user requests. It offers tools for managing temple activities and giving devotees a better experience.

## 2.1 Existing System

Many temples today still use old methods to manage their activities. These methods have several problems:

1. **Paper-based Records**: Most temples use paper notebooks or files to record seva bookings, donations, and events. This makes it hard to find information quickly and can lead to lost or damaged records.

2. **Manual Seva Booking**: Devotees often have to visit the temple in person to book sevas. This is time-consuming and can cause scheduling conflicts if multiple people try to book the same seva at the same time.

3. **Basic Spreadsheets**: Some temples use simple spreadsheets to track donations and events. While this is better than paper records, spreadsheets are not designed for temple management and lack important features.

4. **No Online Presence**: Many temples don't have a good website or online system for devotees to book sevas or make donations. This makes it hard for devotees who can't visit the temple regularly.

5. **Limited Communication**: Temples struggle to keep devotees updated about events, seva schedules, and other important information. This leads to poor attendance at events and missed opportunities.

6. **Lack of Reports**: Without good digital tools, temples can't easily generate reports on donations, seva bookings, and other activities. This makes it hard to plan for the future and make good decisions.

7. **Security Issues**: Paper records and basic spreadsheets offer little security for sensitive information like donation records and user details.

These problems make temple management inefficient and create a poor experience for both temple administrators and devotees. Temple Management System is designed to solve these problems by providing a complete digital solution for temple management.

## 2.2 Proposed System

Temple Management System addresses these problems by providing a complete temple management system with these improvements:

- **Online Seva Booking**: Devotees can book sevas online, view their booking history, and get email confirmations. This saves time and prevents scheduling conflicts.

- **Digital Donation Tracking**: Temples can accept online donations, track donation history, and generate receipts. This makes it easier to manage temple finances and thank donors.

- **Event Management**: Temples can create and manage events, send notifications about upcoming events, and let devotees register for events. This helps increase attendance and engagement.

- **Admin Dashboard**: Temple administrators can manage all temple activities from one place, view reports, and manage user accounts. This makes temple management more efficient.

- **Secure Data Storage**: The system uses MongoDB to store data securely and protect sensitive information. This prevents data loss and unauthorized access.

- **User-Friendly Interface**: The system is easy to use on both mobile and desktop devices, making it accessible to people of all technical backgrounds.

- **Email Notifications**: The system sends emails to users about seva bookings, donations, events, and other important updates. This keeps devotees connected with the temple.

## 2.3 Data Flow Diagram

A Data Flow Diagram (DFD) shows how information moves through a system. It helps us understand how data flows between different parts of the system and how users interact with it. For Temple Management System, DFDs help us see how user inputs move through the system and how data is processed. The DFD is a useful tool for understanding the system structure and finding ways to make it better.

### LEVEL 0

The Level 0 DFD shows Temple Management System as a single process that interacts with external entities like Users and the MongoDB Database. Users send login information and requests (like booking a seva or making a donation) to the system. The system then sends back account details, booking confirmations, and other information. The MongoDB Database stores and retrieves data for the system. This high-level diagram shows the basic interactions between the system and external sources.

![FIG 2.1: Temple Management System DFD(Level 0)](images/fig2-1.png)

### LEVEL 1

In the Level 1 DFD, the system is broken into major components: User Authentication & Profile Management, Seva Management, Donation Management, Event Management, and Admin Dashboard. Each of these processes interacts with data stores (like user data and seva data) and communicates with the MongoDB Database to store and retrieve information. This level provides a good overview of how the app works by focusing on important system features like seva booking, donation tracking, and user management.

![FIG 2.2: Temple Management System DFD(Level 1)](images/fig2-2.png)

### LEVEL 2

The Level 2 DFD goes deeper into the key processes from Level 1, breaking them into specific tasks. For example, User Authentication includes verifying login details and sending password reset emails. Seva Management handles tasks like checking seva availability and sending booking confirmations. Donation Management covers accepting payments, generating receipts, and updating donation records. This level shows a more detailed flow of information and operations within each subsystem.

![FIG 2.3: Temple Management System DFD(Level 2)](images/fig2-3.png)

## 2.4 ER Diagram

An Entity-Relationship (ER) diagram shows how different parts of a database are connected. It helps us understand what information we need to store and how different pieces of information relate to each other. For Temple Management System, the main entities include Users, Sevas, Donations, Events, and Admin Settings. Relationships are established based on interactions such as users booking sevas, making donations, and registering for events. The ER diagram helps in designing a structured and efficient database that can store all the information needed for temple management.

![FIG 2.4: Temple Management System ER Diagram](images/fig2-4.png)

# 3. SYSTEM CONFIGURATION

System configuration refers to the hardware and software setup needed to run Temple Management System. It includes the computer equipment needed to develop and run the system, as well as the software programs and tools used to build and manage it. The system configuration ensures that Temple Management System works well, is secure, and can handle many users at once. It also makes sure that the system can grow as needed to handle more data and users in the future.

## 3.1 Hardware Configuration

The hardware configuration for Temple Management System includes the physical equipment needed to develop and run the system. Here are the minimum requirements:

| Specification | Requirement |
|--------------|-------------|
| Processor | Intel Core i3 or higher for smooth operation |
| RAM | Minimum 4GB (8GB recommended) for good performance |
| Storage | At least 10GB of free space for the application and database |
| Network | Reliable internet connection for online features |
| Display | 1366x768 resolution or higher for comfortable viewing |

- **Processor**: An Intel Core i3 or higher processor is needed to run the system smoothly. This ensures that the application can handle multiple users and tasks at the same time without slowing down.

- **RAM**: At least 4GB of RAM is required, but 8GB is recommended for better performance. This allows the system to handle multiple users and tasks without running out of memory.

- **Storage**: At least 10GB of free space is needed to store the application, database, and user data. This ensures that there is enough space for all the information the system needs to store.

- **Network**: A reliable internet connection is needed for online features like email notifications, online donations, and user registration. This ensures that users can access the system from anywhere.

- **Display**: A display with a resolution of 1366x768 or higher is recommended for comfortable viewing of the system interface. This ensures that users can see all the information clearly.

For development, a more powerful computer with better specifications may be needed to handle the development tools and testing environments. For deployment, the hardware requirements depend on the number of users and the amount of data the system needs to handle.

## 3.2 Software Configuration

The software configuration for Temple Management System includes all the programs and tools needed to build and run the system. Here's an overview of the software components:

| Software Component | Configuration/Requirements |
|-------------------|----------------------------|
| Operating System | Windows 10/11, macOS, or Linux |
| Backend Framework | Flask (Python web framework) |
| Frontend Technologies | HTML5, CSS3, JavaScript, Bootstrap |
| Database | MongoDB (NoSQL database) |
| Email Service | Flask-Mail for sending emails |
| Authentication | Flask-Login for user authentication |
| Payment Gateway | Razorpay for online donations |
| Web Server | Gunicorn for production deployment |
| Version Control | Git for code management |

Here's a detailed breakdown of the software configuration:

- **Operating System**:
  - Windows 10/11, macOS, or Linux can be used for development and deployment.
  - The system is designed to work on any modern operating system.

- **Backend Framework**:
  - Flask is used as the main backend framework.
  - It provides a simple and flexible way to build web applications.
  - Flask handles routing, request processing, and response generation.

- **Frontend Technologies**:
  - HTML5 is used for structuring the web pages.
  - CSS3 is used for styling and layout.
  - JavaScript is used for interactive features.
  - Bootstrap is used for responsive design and UI components.

- **Database**:
  - MongoDB is used as the database system.
  - It's a NoSQL database that stores data in a flexible, document-based format.
  - MongoDB is good for handling large amounts of data and scaling as needed.

- **Email Service**:
  - Flask-Mail is used to send emails for notifications and confirmations.
  - It integrates with the Flask framework for easy email handling.

- **Authentication**:
  - Flask-Login is used for user authentication, ensuring that only authorized users can access protected parts of the system. It includes features like password hashing, session management, and secure login/logout.

- **Payment Gateway**:
  - Razorpay is used for processing online donations.
  - It provides a secure way to accept payments from users.

- **Web Server**:
  - Gunicorn is used as the production web server.
  - It's a Python WSGI HTTP server that's good for production deployment.

- **Version Control**:
  - Git is used for version control and code management.
  - It helps track changes to the code and collaborate with other developers.

The software configuration is designed to be flexible and scalable, allowing the system to grow and adapt as needed. It uses modern technologies that are well-supported and have good documentation, making it easier to maintain and update the system in the future. 