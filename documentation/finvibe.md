## PROJECT REPORT ON

## FinVibe

## Submitted in partial fulfillment of the requirements for Software

## Engineering Mini Project Lab for 2nd Semester

## Master of Computer Science

## Submitted by

## Himanshi Singh 24MCAA

## Shilpa Soni 24MCAA

## Under the guidance of

## Ms. Anju Pavithran


## CERTIFICATE

## This is to certify that the project titled FinVibe has been satisfactorily

## completed by Ms. Himanshi Singh with Reg. No. 24MCAA 27 in partial

## fulfillment of the requirements for Software Engineering Mini Project Lab with

## course code MCC2P2B21, for the 2nd Semester Master of Computer Applications

## course during the academic year 2024-2025 as prescribed by Bangalore North

## University.

## Faculty In-charge Head of the Department

## Valued by

## Examiner 1: Centre: Kristu Jayanti College

## Examiner 2: Date:


## ACKNOWLEDGEMENT

## First of all, we would like to thank the God Almighty for all the blessings he

## has showered on us. Our spiritual quotient gave us more strength and motivation that

## helped immensely.

## We would like to thank Rev. Fr. Dr. Augustine George, our esteemed

## Principal, for providing us their constant guidance and support. I would also like to

## thank Rev. Fr. Lijo P Thomas, our Vice-Principal and Chief Finance Officer, for

## providing us with the best facilities.

## We are extremely thankful to our Dr. Kumar R, Head, Department of

## Computer Science (PG) for giving us the essential support in the form of allocating

## comfortable project hours and necessary software resources.

## We would like to extend our heartfelt thanks to Ms. Anju Pavithran, our

## project guide for providing us the necessary details related to project development

## and process identification enabling us to finish the project within the stipulated time.

## We thank all other faculty members who helped us a lot in completing this

## project.

## We thank our class mates, who have pointed out errors and guided us a lot and

## we thank each and every one who has helped us.


## Synopsis

Overview: FinVibe is an innovative mobile banking and finance management application
designed to provide users with an intuitive and seamless experience for managing their finances.
The app leverages cutting-edge technologies to offer a wide array of services, including real-time
banking transactions, account management, investment tracking, bill payments, financial
insights, and personalized budgeting tools.

Target Audience: FinVibe is aimed at tech-savvy individuals who wish to have full control over
their finances at their fingertips. It caters to young professionals, small business owners,
students, and anyone looking to streamline their financial activities while maintaining high levels
of security and ease of use.

Core Features:

1. Account Management:
    o Check account balances in real time.
    o View detailed transaction history with easy-to-read statements.
    o Add, remove, or manage bank accounts, debit, or credit cards.
2. Financial Insights:
    o Track spending patterns with categorized expense breakdowns.
    o Set monthly budget goals with automatic alerts when nearing limits.
    o Insights into your savings growth and suggestions for improving financial habits.
3. Transactions & Payments:
    o Send and receive money instantly within and outside the bank.
    o Pay utility bills, insurance, and subscriptions through the app.
    o Transfer money to other accounts, manage bill payments, and automate recurring
       transactions.
4. Security:
    o The app uses cutting-edge encryption to ensure that all financial transactions and
       personal data are secure.
5. User-Friendly Interface:


```
o Clean and modern UI built using Bootstrap, HTML, CSS, and Tailwind to
enhance user experience.
o Adaptive to both mobile and desktop devices, offering smooth navigation across
all platforms.
```
6. Customer Support:
    o In-app support chat feature for instant assistance.
    o FAQ section to answer common queries.
    o Contact customer support through phone, email, or in-app messages.

END USERS:The end users of the Banking App with Expense Tracker are individuals who
want to manage their personal finances efficiently. This includes individual users tracking
spending and categorizing expenses, account holders using banking features like checking
balances and transfers, and budget-conscious users setting and monitoring budgets. Tech-savvy
users utilize advanced features like linking multiple accounts and detailed financial reports.
Additionally, financial planners use the app to track savings goals and financial progress. All
users benefit from the app's tools to manage and analyze their finances.


## CONTENTS

## SI. No. Particulars Pg. No

1. Introduction
    1.1 System Definition
    1.2 Project Description

### 1 - 2

### 2.

```
System Study
2.1 Existing System
2.2 Proposed System
2.3 Data Flow Diagram
2.4 ER Diagram
```
### 3 - 8

3. System Configuration
    3.1 Hardware Configuration
    3.2 Software Configuration

### 9 - 12

4. Details of Software
    4.1 Overview of Front End
    4.2 Overview of Back End

### 13 - 14

5. System Design
    5.1 Architectural Design
    5.2 Input Design
    5.3 Output Design
    5.4 Database Design

### 15 - 22


- 6. Source Code 23 -
- 7. Testing^46 -
- 8. Implementation 51 -
- 9. Screen Shot^57 -
- 10. Conclusion
- 11. Bibliography


```
Page | 1
```
## 1. INTRODUCTION

Financial management has become a crucial aspect of modern life, with users seeking seamless,
secure, and efficient ways to handle their banking transactions, budget planning, and expense
tracking. Traditional banking applications often lack intuitive financial insights, real-time updates,
and a user-friendly experience. FinVibe is designed to bridge this gap by providing a feature-rich
mobile banking and finance management application that enables users to track expenses, manage
multiple accounts, pay bills, and receive personalized financial insights.

The application leverages Django for backend development and a modern UI built with Bootstrap,
HTML, CSS, and Tailwind, ensuring a secure, scalable, and efficient financial experience. With
robust security features, real-time transaction updates, and automated budgeting tools, FinVibe
aims to empower users to take full control of their financial well-being.

## 1.1 System Definition

Current financial management and banking applications often lack comprehensive solutions that
integrate real-time transaction updates, financial insights, and secure fund transfers in one
platform. Users often face the following challenges:

- A lack of real-time financial tracking makes it hard to manage expenses.
- Inconvenience of using multiple platforms for banking, bill payments, and budgeting.
- Security vulnerabilities, making users prone to fraud and data leaks.
- Complex, non-intuitive interfaces that hinder seamless navigation and financial planning.
- Lack of personalized financial insights to help users manage expenses and savings
    efficiently.

## 1.2 Project Description

FinVibe is a next-generation mobile banking and finance management application designed to
provide secure, real-time banking features with a user-friendly interface. The application offers:


```
Page | 2
```
- Account Management – Track multiple accounts, check balances, and monitor transaction
    history.
- Financial Insights – Categorized expense tracking, savings growth, and budgeting tools.
- Transactions & Payments – Instant money transfers, bill payments, and automated
    transactions.
- Robust Security – Advanced encryption protocols and fraud detection mechanisms.
- User-Friendly Interface – Clean, modern UI ensuring smooth navigation across devices.

MODULES:

The following modules are typically included in the "FinVibe":

1. User Authentication Module : Manages user registration, login, and security (e.g., password,
two-factor authentication). It ensures secure access to the app.
2. Bank Account Management Module : enables users to view their account balances, view their
transaction history, and carry out banking activities like bill payments or transfers.
3. Expense Tracker Module: Categorizes and tracks expenses automatically or manually,
allowing users to input their spending, view categories (e.g., food, entertainment), and track
financial trends.
4. Budgeting Module: This module lets users set budgets for different categories of expenses and
keeps track of their progress, sending alerts when they get close to or go over limits.
5. Reports & Analytics Module: Provides visual reports, charts, and spending insights, offering
users a detailed view of their financial behavior and trends.
6. Notification Module: Notifies users when their balances are low, when bills are coming up, or
when budget limits are exceeded.


```
Page | 3
```
## 2. SYSTEM STUDY

FinVibe combines banking features (e.g., checking balances, making transfers) with tools to
categorize and monitor personal expenses. It lets users create budgets, keep track of spending, and
look at financial data through charts and reports. Encryption is used to secure data and the system
securely integrates with bank APIs to retrieve transaction data. It offers budgeting tools and
financial insights, helping users make informed decisions.

## 2.1 Existing System

Several existing systems offer similar features to FinVibe, including popular financial
management platforms like Mint, YNAB (You Need A Budget), and Personal Capital. These
applications provide users with real-time transaction updates, expense tracking, multi-account
management, and personalized financial insights[1]. Mint, for example, helps users categorize and
track their spending while offering budgeting tools and bill payment reminders. YNAB[2] focuses
on proactive budgeting and expense management, while Personal Capital combines budgeting with
comprehensive wealth management tools, including investment tracking and retirement planning.
These platforms ensure that users can track their finances easily, set budgets, and receive tailored
financial advice.

Digital banking apps like Revolut, Chime, and Monzo also offer integrated banking features
alongside financial management tools[3]. Revolut, for instance, provides real-time transaction
tracking, automated budgeting, multi-currency support, and seamless bill payments. Chime
focuses on offering fee-free banking services with automatic savings and credit-building tools,

## while Monzo integrates smart budgeting features and personalized savings pots[4]. These systems

combine secure, user-friendly banking services with real-time financial management, making them
ideal choices for users seeking an all-in-one solution for managing their finances effectively.

## 2. 2 Proposed System

FinVibe addresses these limitations by integrating real-time banking, financial planning, and
security features into a single app. The following are significant enhancements: • Real-time
transaction monitoring with categorized expense breakdowns.


```
Page | 4
```
- Automated budgeting tools with alerts for overspending.
- Instant money transfers with enhanced security features.
- Encryption-based security protocols ensuring fraud detection and prevention.
- User-friendly design adaptable for mobile and desktop platforms.

## 2.3 Data Flow Diagram

A Data Flow Diagram (DFD) is a graphical representation used to visualize the flow of data within
a system. It illustrates how information moves between processes, data stores, and external
entities. In the context of the FinVibe, DFDs help break down complex functionalities into clear,
manageable components, showing how user inputs interact with the system and how data is
processed. The DFD serves as a valuable tool for understanding system structure, identifying
potential inefficiencies, and improving overall design. with financial regulations.

LEVEL 0

The Level 0 DFD represents the entire Banking App with Expense Tracker as a single process,
interacting with external entities like the User and the Bank API. The user's login credentials and
transaction requests are inputs to the system, which then outputs account details, balance, and
transaction history. The bank API provides transaction data, and the user interacts with the app to
track expenses and set budgets. This high-level diagram shows the basic interactions between the
system and external sources.

```
FIG 2.1: DFD(Level 0)
```

```
Page | 5
```
### LEVEL 1

In the Level 1 DFD, the system is broken into major components: User Authentication & Profile
Management, Bank Account Management, Expense Tracker, Budget Management, and Reports
& Insights. Each of these processes interacts with data stores (like user data and expense data)
and communicates with the Bank API to fetch transaction information. This level provides a
concise overview of the app's operation by concentrating on important system features like
transaction retrieval, budget tracking, and login.

```
FIG 2.2:DFD(Level 1)
```

```
Page | 6
```
### LEVEL 2

The Level 2 DFD delves deeper into the key processes from Level 1, breaking them into specific
tasks. For instance, User Authentication includes verifying credentials and generating
authentication tokens. Expense Tracker handles tasks like categorizing transactions and allowing
manual expense inputs. Budget Management covers budget creation, progress tracking, and
sending alerts. This level shows a more detailed flow of information and operations within each
subsystem.

```
FIG 2.3:DFD(Level 2)
```
## 2.4 ER Diagram

An Entity-Relationship (ER) diagram is a conceptual data modeling technique used to visually
represent the structure of a database. It illustrates the entities (objects or concepts) involved in the
system, their attributes (characteristics or properties), and the relationships between them. In
Project Ease, the main entities include Users, Projects, Tasks, and Workspaces. Relationships are
established based on interactions such as users creating tasks, assigning tasks to projects, and
collaborating within workspaces. The ER diagram helps in designing a structured and efficient
database schema, ensuring data consistency, integrity, and scalability.


```
Page | 7
```
### FIG 2.4 : ER DIAGRAM


```
Page | 8
```
## 3. SYSTEM CONFIGURATION

System configuration refers to the arrangement of hardware and software components that make
up the FinVibe. It involves the selection of suitable servers, databases, and APIs for managing
user data, transactions, and budget tracking features. The system will be hosted on a secure
platform, ensuring data protection through encryption and secure communication protocols. In
addition, it entails setting up the admin interface for system management and ensuring device
compatibility for a seamless user experience. The app's scalability, security, and efficiency are all
guaranteed by the system configuration.

## 3.1 Hardware Configuration

The application requires the following minimum hardware specifications for optimal performance:

```
Specification Requirement
```
```
Processor Quad-core 2.5 GHz or higher for efficient
multitasking and real-time processing.
RAM Minimum 8 GB to ensure smooth
performance and efficient data handling.
Storage Minimum 256 GB SSD for fast read/write
operations and reliable data storage.
Compatibility Compatible with mobile (Android, iOS)
and web platforms for seamless access.
```
- Processor: A Quad-core 2.5 GHz or higher processor is required to handle multiple tasks
    efficiently, such as real-time transaction processing and data handling. This ensures smooth
    performance even during peak usage and ensures responsive user interactions.


```
Page | 9
```
- RAM: A minimum of 8 GB of RAM is necessary for seamless multitasking and efficient
    data processing. It allows the application to manage large amounts of user data and perform
    complex operations without lag, ensuring smooth overall performance.
- Storage: A 256 GB SSD is recommended for faster data access and reliable storage. SSDs
    provide quicker read/write speeds compared to traditional hard drives, which is crucial for
    storing transaction history, user data, and application files without performance
    degradation.
- Compatibility: The application should be compatible with both mobile (Android and
    iOS) and web platforms. This ensures accessibility across a wide range of devices,
    providing a consistent and responsive user experience whether on mobile or desktop.

## 3.2 Software Configuration

The software configuration of the FinVibe includes the selection and setup of various software
components to ensure smooth operation and functionality. Here’s an overview:

```
Software Component Configuration/Requirements
Operating System Windows 10/11 (for development); macOS (for iOS
development); Linux (optional for server-side)
Backend Framework Django (latest stable version) for scalable backend
development
Frontend Framework Bootstrap, Tailwind CSS, and HTML5 for responsive,
mobile-friendly UI.
```
Database (^) PostgreSQL or MySQL (recommended
for production); SQLite (for
development).


```
Page | 10
```
```
Mobile Development Platforms Xcode (for iOS development); Android Studio (for
Android development)
```
```
Web Server Nginx or Apache for production deployment; Gunicorn
as the WSGI server for Django.
APIs and Third-Party
Integrations
```
```
Integration with Plaid, Stripe, or Galileo for financial
data and payment processing.
```
Here’s a concise breakdown of the software configuration for FinVibe:

- Operating System:
    o Windows 10/11 for development, macOS for iOS development (using Xcode), and
       Linux for production environments and server-side operations.
- Backend Framework:
    o Django is used for the backend, offering a secure, scalable solution for handling
       user authentication, financial transactions, and real-time updates.
- Frontend Framework:
    o Bootstrap and Tailwind CSS are utilized for responsive design and customizable
       UI, ensuring a seamless experience on both mobile and web platforms.
- Database:
    o PostgreSQL is recommended for production due to its scalability and support for
       complex queries, while SQLite can be used for local development.
- Mobile Development Platforms:
    o Xcode (iOS) and Android Studio (Android) are used for developing native mobile
       apps, ensuring compatibility with both platforms.
- Web Server:


```
Page | 11
```
```
o Nginx or Apache is used to serve the app in production, while Gunicorn handles
the Django application server for efficient request processing.
```
- APIs and Third-Party Integrations:

```
o Plaid for bank account integration, Stripe for payments, and Galileo for banking
services provide secure, real-time financial data access and transaction handling.
```

```
Page | 12
```
## 4. DETAILS OF THE SOFTWARE

The software for the FinVibe is designed to ensure seamless user experience, robust functionality,
and secure financial management. It consists of a frontend built with frameworks like React Native
or Flutter for cross-platform compatibility, and a backend using Node.js or Django to handle user
data and transactions. Using Firebase or similar tools, the app provides features like budget
management and real-time notifications in addition to integrating with external bank APIs to
retrieve transaction data. Security measures like data encryption, user authentication, and role-
based access are implemented to safeguard sensitive financial information.

## 4.1 Overview of Frontend

The frontend of FinVibe is designed to be visually appealing, intuitive, and responsive, providing
users with an engaging financial management experience. It leverages modern technologies and
features:

- Bootstrap & Tailwind CSS: Bootstrap (v4.3.1) offers a responsive grid and components
    like tables and buttons, while Tailwind CSS enables flexible, utility-based styling (e.g.,
    flex, shadow-md). Together, they ensure a polished, adaptable UI across devices.
- HTML & CSS: HTML5 provides the structure, enhanced by CSS3 with gradients (e.g.,
    linear-gradient(135deg, #F0F9FF, #E0F2FE)), animations (e.g., bounceIn), and custom
    variables (e.g., --primary-color) for consistent theming.
- Mobile-First Design: Optimized for mobile users, FinVibe uses media queries (e.g.,
    @media (max-width: 768px)) to adjust layouts, ensuring smooth navigation on smaller
    screens.

The interface includes:

- Dashboard: Shows account balance, spending charts (via Chart.js), and the latest
    transaction, with animated stat cards (e.g., fadeInUp) for key metrics.
- Transaction Page: Supports fund transfers and bill payments with a clear table layout and
    interactive buttons (e.g., gradient-styled with hover effects).


```
Page | 13
```
- Expense Tracker: Displays income/expense summaries and a transaction list, using visual
    cues like color-coded amounts and subtle animations.
- Budgeting Tools: Allows goal-setting with alerts (e.g., styled with #F472B6) when
    nearing limits, enhancing financial control.

## 4 .2 Overview of Backend

The backend of FinVibe ensures secure data management, transaction processing, and user
authentication, built with robust tools:

- Django Framework (Python):Django provides a secure, scalable backend with URL
    routing, form handling, and ORM for managing models like Account and Transaction.
- API Integration: External APIs enable banking operations (e.g., transfers, payments),
    integrated via Django REST endpoints for real-time updates.
- Security Mechanisms: Features encryption (e.g., TLS), Django’s authentication (e.g.,
    hashed passwords), and fraud detection (e.g., transaction monitoring) to protect data.


```
Page | 14
```
## 5. SYSTEM DESIGN

The FinVibe's "system design" involves organizing the software architecture to guarantee security,
efficiency, and scalability. It includes defining the overall system architecture, such as frontend
and backend components, and how they communicate with each other. The design focuses on user
experience, ensuring easy navigation for setting budgets, tracking expenses, and viewing reports.
It also incorporates robust security features like data encryption, user authentication, and secure
API integrations. The system design aims to provide a reliable, intuitive platform for both users
and administrators.

## 5.1 Architectural Design

The FinVibe application is designed using a multi-layered architecture to ensure scalability,
security, and seamless user experience across mobile and web platforms. It integrates backend
services, frontend interfaces, third-party APIs, and real-time transaction processing to provide a
secure and efficient financial management solution.

```
Fig:5. 1 Architectural Design
```

```
Page | 15
```
1. Frontend Layer (UI/UX)
    - Web Application: Built using HTML5, Bootstrap, and Tailwind CSS for a responsive and
       interactive user interface, ensuring a seamless experience across mobile, tablet, and
       desktop platforms.
    - Mobile Application: Native apps for Android (developed with Android Studio) and iOS
       (developed with Xcode) ensure optimized and platform-specific functionality for
       managing finances on the go.
2. Backend Layer (Business Logic)
    - Django Framework: The backend is powered by the Django framework, a secure and
       scalable solution that handles user management, transaction processing, and real-time
       updates. Django's REST API handles requests such as fetching transactions, linking bank
       accounts, and initiating payments.
    - Gunicorn: A WSGI server used in combination with Django to process HTTP requests
       efficiently.
3. Database Layer
    - PostgreSQL: The primary database for storing user data, transactions, and account
       information. PostgreSQL provides robust data integrity, scalability, and efficient query
       handling, making it suitable for managing complex financial data.
    - SQLite: Used during development for lightweight database needs.
4. Third-Party Integrations
    - Plaid API: Plaid is integrated to securely link users' bank accounts, fetch real-time
       transaction data, and ensure seamless data aggregation across various banks.
    - Stripe API: Stripe is used for secure payments, bill payments, and financial transactions,
       enabling users to transfer funds and manage bills directly within the app.


```
Page | 16
```
- Galileo API: Provides Banking-as-a-Service (BaaS), offering functionalities like account
    management, payments, and money transfers.
5. Security Layer
- SSL/TLS Encryption: Ensures secure data transmission between the frontend and backend,
protecting sensitive financial information from cyber threats.
- OAuth 2.0 & JWT: Used for secure user authentication and session management. OAuth
allows third-party access to accounts securely, while JWT ensures token-based user
authentication.
6. Web and Mobile Servers
- Nginx/Apache Web Server: In production, Nginx or Apache is used as a reverse proxy
server, handling user requests and forwarding them to the application server.
- Gunicorn: Serves the Django app for HTTP request processing and response handling,
ensuring smooth interactions between the client and backend services.
7. Containerization and CI/CD
- Docker: Docker is employed to containerize the application, ensuring consistency and
reliability across different environments (development, testing, production).
- CI/CD Pipeline: GitHub or GitLab is used for version control, with automated pipelines
for continuous integration, testing, and deployment to production.

```
FinVibe's architecture provides a robust, secure, and scalable solution for managing user
finances, handling sensitive data with high performance and minimal latency. The
modularity of the design ensures that it can evolve with new features and integrations while
maintaining security and user experience at the core.
```

```
Page | 17
```
## 5.2 Input Design

Inputs should be intuitive, validated, and secure to ensure smooth operations.

**User Inputs:**

- Name, Email & Password (Login/Register)
- Add Accounts (Account Holder name, Amount, CVV, Account No.)
- Transfer Money (Sender Name, Source account, CVV,Reciver Name ,Reciver Account
    No.,Amount)
- Expenses(Source Account, Description, Amount,type of Expense)

System Inputs (Automated):

- Deadline Notifications (push notifications)

Fig:5. 2 Log in Page Design

Fig: 5. 3 Sign up Page Design


```
Page | 18
```
```
Fig: 5. 4 Add Account Page Design
```
## 5.3 Output Design

Outputs should be real-time, visually structured, and accessible across devices.

**User Outputs:**

- **Dashboard** – Overview of active transactions and line chart.
- **Transaction** – transaction display the all the transactions happened till date.
- **Notifications** – , push notification for the expenses alert.
- **User Profile & Activity Logs** – Displays user details a.

**System Outputs (Logs & Reports):**

- **Transaction report** – User Recent transaction Report.
- **Espenses Record** – User All Expenses Record


```
Page | 19
```
```
Fig: 5. 5 Account Page Design
```
Fig: 5. 6 Transaction History Page


```
Page | 20
```
## 5.4 Database Design

## User Table

The User Table contains the fundamental information for each user, such as a unique identifier
(ID), the user's full name, email address (used for login), and a hashed password for secure

## authentication. It is essential for managing user accounts and securing access to the system.

```
Column
```
## Data Type Constraint Description

## id UUID^ PRIMARY KEY^ Unique identifier for each user^

```
name VARCHAR NOT NULL Full name of user
email VARCHAR UNIQUE , NOT NULL Used for login
password VARCHAR NOT NULL Hashed password for
authentication
```
## Account Table

The Account Table stores information related to individual bank accounts, including account
holder name, account number, CVV, and the account balance. It links accounts to users and ensures

## the correct management of funds for transactions.

## Column Type Constraint Description

```
id UUID PRIMARY KEY Unique identifier
account holder
name
```
```
VARCHAR NOT NULL Name of the account holder
```
```
Account no. int NOT NULL Account no.
```

```
Page | 21
```
```
cvv UUID(Foreign
key)
```
```
FOREIGN KEY Cvv no.
```
```
amount float NOT NULL amount
```
## Transaction Table (Kanban board)

The Transaction Table records details of all financial transactions, including sender and receiver
information, account numbers, CVV for security, transaction amounts, and the recipient's account
number. It tracks the flow of money within the system.

## Column Data Type Constraints Description

```
Reciver;s Name VARCHAR NOT NULL Name of the recipient of the
transaction
Sender’s name VARCHAR NOT NULL Name of the sender or account
holder making the transaction.
Account no. int NOT NULL Account number of the sender
involved in the transaction.
cvv UUID FOREIGN KEY References the CVV number
from the Account Table
(foreign key).
amount float NOT NULL Transaction amount (can be
positive or negative).
Reciver Account no int NOT NULL Account number of the recipient
(receiver).
```

```
Page | 22
```
## Expenses Table

The Expenses Table tracks individual expenses made from a user's account, categorizing each
transaction with a description and type (positive for income, negative for expenses). It helps users
monitor and analyze their spending patterns.

## Column Type Constraint Description

```
Source
Account
```
```
int NOT NULL Account number from which the expense
is deducted.
Description text NOT NULL Brief description of the expense (e.g.,
food, movie).
Type of
Expense
```
```
int NOT NULL Type of expense; positive (+ve) for
income, negative (-ve) for expense.
amount float NOT NULL The amount spent or earned.
```

```
Page | 23
```
## 6.SOURCE CODE

Source code is the foundation of any project. It is the collection of human-written code which
programmers write to build a project. It tells the computer what to do and how to do, step-by-step.
It defines the behavior of the project and helps in handling the input from the user, process it and
provides the output. It can be written in any programming language like Java, C, C++, Python etc.
Source code also helps to handle the frontend and backend of the project and helps in collaboration
with other developers.

## Login.html

<!DOCTYPE html>

<html lang="en">

<head>

<title>Login Page</title>

<link rel="preconnect" href="https://fonts.gstatic.com">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-
awesome/5.15.4/css/all.min.css">

<link
href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=swap"
rel="stylesheet">

<!--Stylesheet-->

<style media="screen">

*,

*:before,

*:after{

padding: 0; margin: 0; box-sizing: border-box;


```
Page | 24
```
### }

body{

background-color: #080710;

}

.background{

width: 430px; height: 520px; position: absolute; transform: translate(-50%,-50%); left: 50%;

top: 50%;

}

.background .shape{

height: 200px; width: 200px; position: absolute; border-radius: 50%;

}

.shape:first-child{

background: linear-gradient( #1845ad, #23a2f6 ); left: -80px; top: -80px;

}

.shape:last-child{

background: linear-gradient(to right, #ff512f, #f09819 ); right: -30px; bottom: -80px;

}

form{

height: 520px; width: 400px; background-color: rgba(255,255,255,0.13); position: absolute;

transform: translate(-50%,-50%); top: 50%; left: 50%; border-radius: 10px; backdrop-filter:

blur(10px); border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 0 40px rgba(8,7,16,0.6);


```
Page | 25
```
padding: 50px 35px;

}

form *{

font-family: 'Poppins',sans-serif; color: #ffffff; letter-spacing: 0.5px; outline: none; border:

none;

}

form h3{

font-size: 32px; font-weight: 500; line-height: 42px; text-align: center;

}

label{

display: block; margin-top: 30px; font-size: 16px; font-weight: 500;

}

input{

display: block; height: 50px; width: 100%; background-color: rgba(255,255,255,0.07); border-

radius: 3px; padding: 0 10px; margin-top: 8px; font-size: 14px; font-weight: 300;

}

::placeholder{

color: #e5e5e5;

}

button{

margin-top: 50px; width: 100%; background-color: #ffffff; color: #080710; padding: 15px 0;


```
Page | 26
```
font-size: 18px; font-weight: 600; border-radius: 5px; cursor: pointer;

}

.social{

margin-top: 30px; display: flex;

}

.social div{

background: red; width: 150px; border-radius: 3px; padding: 5px 10px 10px 5px; background-

color: rgba(255,255,255,0.27); color: #eaf0fb; text-align: center;

}

.social div:hover{

background-color: rgba(255,255,255,0.47);

}

.social .fb{

margin-left: 25px;

}

.social i{

margin-right: 4px;

}

</style>

</head>


```
Page | 27
```
<body>

<div class="background">

<div class="shape"></div>

<div class="shape"></div>

</div>

<form method="post">

<h3>Login Here</h3>

{% csrf_token %}

<label for="username">Username</label>

<input type="text" placeholder="Enter Username" id="username" name="username">

<label for="password">Password</label>

<input type="password" placeholder="Password" id="password" name="pass">

<button type="submit">Log In</button>

<!-- <input type="button" value=""> -->

<!-- <div class="social">

<div class="go"><i class="fab fa-google"></i> Google</div>

<div class="fb"><i class="fab fa-facebook"></i> Facebook</div>

</div> -->

<a href="{% url 'signup' %}" >Create a account</a>


```
Page | 28
```
</form>

</body>

</html>

## Signup.html

<!DOCTYPE html>

<html lang="en">

<head>

<title>Signup Page</title>

<link rel="preconnect" href="https://fonts.gstatic.com">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-
awesome/5.15.4/css/all.min.css">

<linkhref="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=s
wap" rel="stylesheet">

</head>

<body>

<div class="background">

<div class="shape"></div>

<div class="shape"></div>

</div>

<form action="" method="post">

{% csrf_token %}


```
Page | 29
```
<h3>Signup Here</h3>

<label for="username">Username</label>

<input type="text" placeholder="Username" name="username" id="username">

<label for="email">Email</label>

<input type="email" placeholder="Email or Phone" name="email" id="email">

<label for="password1">Password</label>

<input type="password" placeholder="Password" id="password1" name="password1">

<label for="password2">Confrom Password</label>

<input type="password" placeholder="Confrom Password" id="password2"
name="password2">

<button type="submit">Signup</button>

<a href="{% url 'login' %}" >i have already account</a>

</form>

</body>

</html>

## Home.html

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">


```
Page | 30
```
<link rel="stylesheet"
href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<title>Banking Dashboard</title>

</head>

<body>

<div class="dashboard">

<div class="sidebar">

<a href="{% url 'home' %}"><i class="bx bx-home"></i> Home</a>

<a href="{% url 'transactions' %}"><i class="bx bx-transfer"></i> Transactions</a>

<a href="{% url 'view_accounts' %}"><i class="bx bx-credit-card"></i> Accounts</a>

<a href="{% url 'transfer' %}"><i class="bx bx-money"></i> Transfer</a>

<a href="{% url 'expenses' %}"><i class="bx bx-line-chart"></i> Expenses</a>

<a href="{% url 'logout' %}"><i class="bx bx-log-out"></i> Logout</a>

</div>

<div class="main-content">

<div class="header">

<h1><b>Welcome, {{ request.user.username|title }}!</b></h1>

</div>


```
Page | 31
```
<div class="stats">

<div class="stat-card">

<h3>Account Balance</h3>

<p>${{ total_balance|floatformat:2 }}</p>

</div>

<div class="stat-card">

<h3>Total Transactions</h3>

<p>{{ transactions.count }}</p>

</div>

<div class="stat-card">

<h3>Recent Activity</h3>

<p>{{ transactions.count }}</p>

</div>

</div>

<div class="transactions">

<h3><b>Recent Transactions</b></h3>

<ul>

{% for transaction in transactions|slice:":5" %}

<li>

<span>{{ transaction.description|truncatechars:20 }}</span>


```
Page | 32
```
<span class="{% if transaction.amount < 0 %}text-red-500{% else %}text-
green-500{% endif %}">

${{ transaction.amount|floatformat:2 }}

</span>

</li>

{% empty %}

<li>No recent transactions.</li>

{% endfor %}

</ul>

<div class="chart-container">

<canvas id="transactionChart"></canvas>

</div>

</div>

</div>

<div class="profile-sidebar">

<div class="username">

{% if request.user.is_authenticated %}

{{ request.user.username|title }}

{% else %}

Guest User

{% endif %}


```
Page | 33
```
</div>

</div>

</div>

</body>

</html>

## Accounts.html

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<!-- Bootstrap CSS -->

<link rel="stylesheet"
href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css">

<!-- Tailwind CSS -->

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">

<title>View Accounts</title>

</head>

<body>

<div class="dashboard">


```
Page | 34
```
<div class="sidebar">

<a href="{% url 'home' %}"><i class="bx bx-home"></i> Home</a>

<a href="{% url 'transactions' %}"><i class="bx bx-transfer"></i> Transactions</a>

<a href="{% url 'view_accounts' %}"><i class="bx bx-credit-card"></i> Accounts</a>

<a href="{% url 'transfer' %}"><i class="bx bx-money"></i> Transfer</a>

<a href="{% url 'expenses' %}"><i class="bx bx-line-chart"></i> Expenses</a>

<a href="{% url 'logout' %}"><i class="bx bx-log-out"></i> Logout</a>

</div>

<div class="main-content">

<div class="container">

<h2 class="text-xl font-semibold mb-4">All Bank Accounts</h2>

{% if messages %}

{% for message in messages %}

<div class="alert alert-{{ message.tags }}">{{ message }}</div>

{% endfor %}

{% endif %}

<table class="table table-striped">

<thead class="thead-dark">

<tr>

<th>#</th>

<th>Account Holder</th>


```
Page | 35
```
<th>Bank Name</th>

<th>Account Number</th>

<th>Account Type</th>

<th>Balance</th>

</tr>

</thead>

<tbody>

{% for account in accounts %}

<tr>

<td>{{ forloop.counter }}</td>

<td>{{ account.account_holder_name }}</td>

<td>{{ account.bank_name }}</td>

<td>{{ account.account_number }}</td>

<td>{{ account.account_type }}</td>

<td>${{ account.amount }}</td>

</tr>

{% empty %}

<tr>

<td colspan="6" class="text-center">No accounts added yet.</td>

</tr>

{% endfor %}


```
Page | 36
```
</tbody>

</table>

<a href="{% url 'add_account' %}" class="btn btn-success">Add New Account</a>

</div>

</div>

</div>

</body>

</html>

## Transactions.html

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<link rel="stylesheet"
href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">

<title>Transaction History</title>

</head>

<body>


```
Page | 37
```
<div class="dashboard">

<!-- Sidebar -->

<div class="sidebar">

<a href="{% url 'home' %}"><i class="bx bx-home"></i> Home</a>

<a href="{% url 'transactions' %}"><i class="bx bx-transfer"></i> Transactions</a>

<a href="{% url 'view_accounts' %}"><i class="bx bx-credit-card"></i>
Accounts</a>

<a href="{% url 'transfer' %}"><i class="bx bx-money"></i> Transfer</a>

<a href="{% url 'expenses' %}"><i class="bx bx-line-chart"></i> Expenses</a>

<a href="{% url 'logout' %}"><i class="bx bx-log-out"></i> Logout</a>

</div>

<!-- Main Content -->

<div class="main-content">

<div class="container">

<h1 clasas="text-2xl font-bold text-center mb-4">Transaction History</h1>

<table class="table table-bordered table-striped">

<thead class="thead-dark">

<tr>

<th>Date</th>

<th>Description</th>


```
Page | 38
```
<th>Amount</th>

<th>Status</th>

</tr>

</thead>

<tbody>

{% for transaction in transactions %}

<tr>

<td>{{ transaction.date }}</td>

<td>{{ transaction.description }}</td>

<td>${{ transaction.amount }}</td>

<td class="{% if transaction.status == 'completed' %}text-success{% elif
transaction.status == 'pending' %}text-warning{% else %}text-danger{% endif %}">

{{ transaction.get_status_display }}

</td>

</tr>

{% empty %}

<tr>

<td colspan="4" class="text-center">No transactions found.</td>

</tr>

{% endfor %}

</tbody>


```
Page | 39
```
</table>

</div>

</div>

</div>

</body>

</html>

## Transfer.html

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<link rel="stylesheet"

href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">

<title>Payment Transfer</title>

</head>

<body>

<div class="dashboard">

<div class="sidebar">


```
Page | 40
```
<a href="{% url 'home' %}"><i class="bx bx-home"></i> Home</a>

<a href="{% url 'transactions' %}"><i class="bx bx-transfer"></i> Transactions</a>

<a href="{% url 'view_accounts' %}"><i class="bx bx-credit-card"></i> Accounts</a>

<a href="{% url 'transfer' %}"><i class="bx bx-money"></i> Transfer</a>

<a href="{% url 'expenses' %}"><i class="bx bx-line-chart"></i> Expenses</a>

<a href="{% url 'logout' %}"><i class="bx bx-log-out"></i> Logout</a>

</div>

<div class="form-group">

<label for="id_receiver_name">Receiver Name</label>

<i class="bx bx-user"></i>

{{ form.receiver_name }}

</div>

<div class="form-group">

<label for="id_receiver_account_no">Receiver Account Number</label>

<i class="bx bx-hash"></i>

<input type="text" name="receiver_account_no" id="id_receiver_account_no"

class="form-control" placeholder="Enter receiver's account number" required>

</div>

<div class="form-group">

<label for="id_recipient_account">Recipient Account</label>

<i class="bx bx-wallet"></i>


```
Page | 41
```
{{ form.recipient_account }}

</div>

<div class="form-group">

<label for="id_amount">Amount</label>

<i class="bx bx-money"></i>

{{ form.amount }}

</div>

<div class="form-group">

<label for="id_sender_cvv">Sender CVV Number</label>

<i class="bx bx-lock-alt"></i>

<input type="text" name="sender_cvv" id="id_sender_cvv" class="form-control"

placeholder="Enter CVV" maxlength="3" required>

</div>

<button type="submit" class="btn-primary">Transfer Funds</button>

</form>

</div>

</div>

</div>

</body>

</html>


```
Page | 42
```
## Expenses.html

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Expense Tracker</title>

<link rel="stylesheet" href = "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/

bootstrap.min.css">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">

</head>

<body>

<div class="dashboard">

<div class="sidebar">

<a href="{% url 'home' %}"><i class="bx bx-home"></i> Home</a>

<a href="{% url 'transactions' %}"><i class="bx bx-transfer"></i> Transactions</a>

<a href="{% url 'view_accounts' %}"><i class="bx bx-credit-card"></i> Accounts</a>

<a href="{% url 'transfer' %}"><i class="bx bx-money"></i> Transfer</a>

<a href="{% url 'expenses' %}"><i class="bx bx-line-chart"></i> Expenses</a>

<a href="{% url 'logout' %}"><i class="bx bx-log-out"></i> Logout</a>


```
Page | 43
```
</div>

<div class="main-content">

<div class="container">

<h2>Expense Tracker</h2>

{% if messages %}

{% for message in messages %}

<div class="alert alert-{{ message.tags }}">{{ message }}</div>

{% endfor %}

{% endif %}

<h4>Your Balance</h4>

<h1 id="balance">${{ total_balance|floatformat:2 }}</h1>

<div class="d-flex justify-content-between bg-white p-3 shadow-md rounded">

<div class="text-center">

<h4>Income</h4>

<p id="money-plus" class="text-green-500 font-bold">+${{ income|floatformat:2
}}</p>

</div>

<div class="text-center">

<h4>Expense</h4>

<p id="money-minus" class="text-red-500 font-bold">-${{
expenses|floatformat:2 }}</p>

</div>


```
Page | 44
```
</div>

<h3 class="mt-4">History</h3>

<ul id="list" class="list-group">

{% for transaction in transactions %}

<li class="list-group-item {% if transaction.amount < 0 %}text-red-500{% else

%}text-green-500{% endif %}">

{{ transaction.description }} <span>${{ transaction.amount|floatformat:2 }}</span>

</li>

{% empty %}

<li class="list-group-item">No transactions yet.</li>

{% endfor %} </ul>

<h3 class="mt-4">Add new transaction</h3>

<form method="POST">

{% csrf_token %}

<div class="form-group">

<label for="id_source_account">Source Account</label>

{{ form.source_account }}

</div>

<div class="form-group">

<label for="id_description">Description</label>

{{ form.description }}


```
Page | 45
```
</div>

<div class="form-group">

<label for="id_amount">Amount</label>

{{ form.amount }}

</div>

<div class="form-group">

<label for="id_transaction_type">Transaction Type</label>

{{ form.transaction_type }}

</div>

<button type="submit" class="btn-primary">Add transaction</button>

</form>

</div>

</div>

</div>

</body>

</html>


```
Page | 46
```
## 6. TESTING

Testing is the process of checking whether the software is working as expected. It helps in finding
and fixing bugs, which is a very important aspect of testing. It also ensures the reliability and
efficiency of the software. There are many types of testing done on a project before making it
available to the end-user. Every test has its own parameters that must be met. Testing helps in
making the software more reliable, bug free and improve the quality of the software. It also reduces
the risk of failure in the long run.

Validation Testing

Functional testing checks whether the software meets user requirements as in real-world
scenarios. It focuses on building the software correctly. This type of testing increases user
satisfaction and reduces issued later in the future.

## 1. Check Login Credentials after giving correct Username and Password:

```
FIG 7. 2 - Login Page Success
```
FIG 7.1-Login Page


```
Page | 47
```
```
Fig 7.3:User Dashboard
```
2.Check Login Credentials after giving incorrect Username and Password:

```
Fig 7.4: Login Unsuccessful
```
Integration Testing
Integration testing is a type of testing where two or more modules of a system are tested together
to check whether they perform as expected. It mainly focuses on interaction between units or
modules. It is performed by developers or testers. It is performed once all the modules go through
unit testing. It also helps to find the error during the initial phase of development.

## Functional Testing

Functional testing checks whether the software meets its requirements by testing its
functionalities and ensures that they work as expected. It is only concerned with the results of
processing.


```
Page | 48
```
1.Check Adding Account successfully:

```
Fig 7.5:Adding a Bank Account
```
```
FIG 7.6 Bank Account Added Successful
```

```
Page | 49
```
2. Check Money Transfer with sufficient balance successfully:

```
FIG 7. 7 Payment Transfer Page
```
```
FIG 7. 8 Payment Transfer Successfull
```

```
Page | 50
```
3. Check Money Transfer with insufficient balance :

```
Fig 7. 9 Payment Transfer Failed
```
```
Fig 7. 10 Transaction History Page
```
Integration Testing
Integration testing is a type of testing where two or more modules of a system are tested together
to check whether they perform as expected. It mainly focuses on interaction between units or
modules. It is performed by developers or testers. It is performed once all the modules go through
unit testing. It also helps to find the error during the initial phase of development


```
Page | 51
```
## 8. Implementation 51 -

## Implementation of the Banking System

```
The implementation steps ensure that the Banking System is properly installed, deployed, and
configured for the client's use. This includes system requirements, installation procedures, and user
configuration.
```
## 1. System Requirements

```
To properly implement the system, the client needs the following:
```
```
Hardware Requirements:
```
- Processor: Intel i3 or above.
- RAM: 4GB (minimum); 8GB+ (recommended).
- Storage: At least 10GB of free space.
- Network: A reliable internet connection for development and testing (optional for local
    deployment).

```
Software Requirements:
```
- Operating System: Windows, macOS, or Linux.
- Python: Version 3.8 or higher (includes pip).
- Database: SQLite (default, embedded with Django; MySQL/PostgreSQL optional).
- Browsers: Chrome, Firefox, Edge, or Safari.
- Code Requirements: Django 5.1.7+, Python 3.8+.

## 2. Installation and Configuration Steps

```
Step 1: Set Up the Environment
```
- Install Python if not already present:
    o Download from python.org.


```
Page | 52
```
```
o Verify: python --version.
```
- Create and activate a virtual environment:
    o Windows:

```
bash
```
```
CollapseWrapCopy
```
```
python -m venv my_venv
```
```
my_venv\Scripts\activate
```
```
o Linux/macOS:
```
```
bash
```
```
CollapseWrapCopy
```
```
python3 -m venv my_venv
```
```
source my_venv/bin/activate
```
- Install Django:

```
bash
```
```
CollapseWrapCopy
```
```
pip install django
```
Step 2: Configure the Project

- Create the Django project:

```
bash
```
```
CollapseWrapCopy
```

```
Page | 53
```
```
django-admin startproject bank.
```
- Create the banking app:

```
bash
```
```
CollapseWrapCopy
```
```
python manage.py startapp banking
```
- Copy the provided code into the respective files:
    o bank/settings.py, bank/urls.py
    o banking/admin.py, banking/forms.py, banking/models.py, banking/views.py
    o Place templates in a templates/ folder at the project root.

Step 3: Database Configuration

- Configure the database in bank/settings.py (SQLite is default):

```
python
```
```
CollapseWrapCopy
```
```
DATABASES = {
```
```
'default': {
```
```
'ENGINE': 'django.db.backends.sqlite3',
```
```
'NAME': BASE_DIR / 'db.sqlite3',
```
```
}
```
```
}
```
- Generate and apply migrations:


```
Page | 54
```
```
bash
```
```
CollapseWrapCopy
```
```
python manage.py makemigrations banking
```
```
python manage.py migrate
```
Step 4: Deploy and Run the System

- Create a superuser for admin access:

```
bash
```
```
CollapseWrapCopy
```
```
python manage.py createsuperuser
```
```
o Example credentials: username: admin, email: admin@example.com, password:
password123.
```
- Start the development server:

```
bash
```
```
CollapseWrapCopy
```
```
python manage.py runserver
```
- Open a browser and navigate to:

```
text
```
```
CollapseWrapCopy
```
```
http://localhost:8000/login/
```
- The login page will appear. Use the superuser credentials or sign up a new user at /signup/.


```
Page | 55
```
Step 5: Verify Functionality

- Test key features:
    o Signup/Login: Create a user and log in.
    o Add Account: Add a bank account at /add_account/.
    o Transfer Funds: Perform a transfer at /transfer/.
    o Expenses: Record income/expenses at /expenses/.
    o View Transactions/Accounts: Check /transactions/ and /accounts/.

## 3. User Roles & Configuration

Admin Role:

- Access: Logs in via /login/ with superuser credentials or admin panel at /admin/.
- Functions:
    o Manage bank accounts (add, update, remove) via /add_account/ or admin panel.
    o View and manage all transactions via /transactions/ or admin panel.
- Configuration: Use createsuperuser to set up.

User Role:

- Access: Logs in via /login/ with personal credentials.
- Functions:
    o Add and view personal bank accounts at /accounts/.
    o Perform transfers at /transfer/.
    o Track expenses/income at /expenses/.
- Configuration: Register via /signup/ and log in.

## 4. Post-Implementation Support & Maintenance

- Regular Backups:
    o Manually back up db.sqlite3 or automate with a script (e.g., copy to a backup folder
       daily).


```
Page | 56
```
- Security Updates:
    o Keep Django updated: pip install --upgrade django.
    o Use a strong SECRET_KEY in production (not the insecure one provided).
- Technical Support:
    o Users can report issues to developers via email or a ticketing system.
    o Debug using Django’s error logs (enable DEBUG = True in settings.py for
       development).


```
Page | 57
```
## 9.SCREEN SHOTS

```
Fig 8.1 Home Page
```
Fig 8. 2 Transaction History Page


```
Page | 58
```
```
Fig 8.3 Add Account Page
```
Fig 8. 4 All Bank Account Page


```
Page | 59
```
# Fig 8.5 Paymet Transfer Page

```
Fig 8.6 Expenses Page
```

```
Page | 60
```
## 10. Conclusion

## FinVibe offers a highly practical and user-friendly solution for individuals who want to manage

their baking costs effectively. By allowing users to set a budget and providing real-time
notifications when they exceed it, the app ensures that users can bake within their financial limits
while still enjoying the process of creating delicious recipes.

## Key highlights of the app include:

- Budget Control: Users can easily set a budget for their baking ingredients and track the
    total cost as they add items. This helps them stay mindful of their spending and avoid
    overspending.
- Real-Time Notifications: The notification system alerts users when their total ingredient
    cost exceeds their set budget, helping them make quick adjustments (e.g., switching to
    cheaper ingredients or reducing quantities).
- Recipe Management: The app also allows users to browse or create recipes, giving them
    the flexibility to track costs while ensuring they stay within their budget.
- User-Friendly Interface: With an intuitive design and real-time updates, users can quickly
    interact with the app and enjoy a smooth experience.

From a technical standpoint, the app’s layered architecture ensures scalability, maintainability,
and flexibility. The clear separation of concerns between the Presentation, Application, Data
Access, and Database layers facilitates easy updates and testing. Additionally, by integrating cost
tracking, notifications, and data management, the app can provide a robust and reliable experience
for users.

Ultimately, this baking app not only empowers users to control their finances but also enhances
their overall baking experience, making it a useful tool for both.


```
Page | 61
```
## 11. Bibliography

## Books

1. Duckett, Jon. HTML & CSS: Design and Build Websites. Wiley, 2011.
2. McFarland, David Sawyer. JavaScript & jQuery: Interactive Front-End Web Development.
    Wiley, 2014.

Online Documentation and Resources

3. Tailwind CSS, 2023, https://tailwindcss.com/docs.
4. Boxicons, v2.1.4, 2023, https://boxicons.com/.
    (Source for the icon library integrated into the sidebar navigation)
5. Chart.js, v4.4.4, 2023, https://www.chartjs.org/docs/latest/.
    (used to create the transaction chart on the dashboard.)

Websites and Tutorials

6. W3Schools, https://www.w3schools.com/html/.
7. CSS-Tricks, 20 Apr. 2020, https://css-tricks.com/snippets/css/a-guide-to-flexbox/.

### .



