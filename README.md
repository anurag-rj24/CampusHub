📌 Problem Statement – CampusHub

Universities and educational institutions handle large volumes of data related to students, faculty, administration, and academic activities. In many institutions, these operations are either manual or managed using multiple disconnected systems, leading to inefficiencies, data inconsistency, lack of transparency, and security concerns.

Students often face difficulty in accessing consolidated information such as their profiles, attendance records, academic results, and leave application status. Faculty members require efficient tools to manage attendance, upload marks, and approve student requests, while administrators need centralized control over user management and system reports. Additionally, higher authorities require visibility into system activities to ensure accountability and security.

Most existing solutions are either:

Too complex for small institutions, or
Do not provide clear role-based access control, or
Lack security features such as password protection and activity tracking.

There is a need for a centralized, secure, and role-based university portal that provides controlled access to information and operations based on user roles, while maintaining scalability for future enhancements.

🎯 Proposed Solution

The proposed system, CampusHub, is a console-based University Management Portal designed using C++, applying Object-Oriented Programming (OOP), Data Structures & Algorithms (DSA), and SQL-based database management concepts.

CampusHub provides:

A single platform for students, faculty, administrators, and system heads
Role-based dashboards ensuring users can only access features relevant to their responsibilities
Secure authentication using password hashing
Audit logging to track critical system activities for accountability

The system is designed with a modular architecture so that it can be extended into a GUI-based or mobile application in the future without major restructuring.

👥 User Roles Covered
Student
View personal profile
View attendance and academic results
Apply for leave and track leave status
Faculty
View assigned subjects and student lists
Mark attendance and upload marks
Approve student leave requests
Admin
Manage student and faculty accounts
View user information and generate reports
Oversee operational activities
Super Head
Manage administrator accounts
View complete system reports
Access audit logs
Perform system-level operations such as database backup



🔐 Key Challenges Addressed
Data Security: Prevents storage of plain-text passwords using hashing techniques
Access Control: Ensures strict role-based permissions
Transparency: Audit logs provide traceability of system actions
Scalability: Object-oriented design allows future expansion to GUI or mobile platforms



✅ Expected Outcome

The CampusHub system aims to:

Simplify university data management
Reduce manual effort and errors
Improve accessibility of academic information
Demonstrate practical application of C++, OOP, DSA, and SQL concepts
Serve as a resume-worthy project suitable for internships and placement opportunities


🔥 Why This Problem Statement is STRONG

✔ Real-world relevance
✔ Clear problem → solution mapping
✔ Mentions security, scalability, and roles
✔ Sounds professional and industry-aligned












Project Objective

Design and implement a console-based, role-based university management system named CampusHub using C++, Object-Oriented Programming (OOP) principles, Data Structures and Algorithms (DSA), and SQL-based persistent storage, with a scalable architecture that allows future migration to GUI or mobile applications.

System Description

CampusHub is a centralized system that manages academic and administrative data for a university. The system supports multiple user roles, each with strictly defined permissions, and ensures secure authentication and activity tracking.

The system operates via a menu-driven console interface and interacts with a relational database to store and retrieve data.

User Roles and Access Control
Roles
Student
Faculty
Admin
SuperHead (highest privilege)

Each role must inherit from a common base user type and must only access features explicitly permitted to that role.

Functional Requirements
Authentication
Users must log in using a username and password.
Passwords must be stored and verified using hashing, not plain text.
On successful login, the system must identify the user role and redirect to the appropriate dashboard.
Student Capabilities
View personal profile (read-only)
View attendance records
View academic results
Submit leave requests
View leave request status
Faculty Capabilities
View personal profile
View assigned subjects
View enrolled students
Mark and update attendance
Upload or update student marks
Approve or reject student leave requests
Admin Capabilities
Create, update, and remove student and faculty user accounts
View all registered users
Generate operational reports
SuperHead Capabilities
Create, update, and remove admin accounts
View complete system reports
View audit logs
Perform system-level actions such as database backup
Audit Logging
The system must record critical actions including:
User login and logout
User creation and deletion
Attendance updates
Marks updates
Each log entry must include:
Timestamp
User role
Action description
Audit logs must only be accessible by SuperHead.
Data Management
Persistent storage must be implemented using SQL.
The system must maintain tables for:
Users
Roles
Attendance
Marks
Leave requests
Audit logs
Non-Functional Requirements
Security
No plain-text passwords
Role-based authorization enforcement
Restricted access to sensitive operations
Scalability
Code must follow modular and object-oriented design
Business logic must be independent of UI logic
Design should allow future GUI/mobile front-end integration
Performance
Use efficient data structures where applicable
Aim for constant-time lookups for authentication and role validation
Constraints
Initial implementation must be console-based
Primary language: C++
Time allocation: 1–2 hours per day
GUI and mobile app implementation are out of scope for the initial phase
Expected Output

A working, menu-driven console application that:

Demonstrates secure authentication
Enforces role-based access
Persists data using SQL
Logs system activities
Is suitable for internship and placement evaluation
Evaluation Criteria
Correct implementation of role hierarchy
Secure handling of authentication
Clean OOP design and modular structure
Logical menu navigation
Extendability to future interfaces