# ROTOSITE
THE WEBSMITHS
ROTOSITE
A comprehensive web application for managing Rotaract club activities, members, events, and announcements.

Table of Contents
Features

Technologies Used

File Structure

Getting Started

Prerequisites

Installation

Usage

Contributing

Features
Admin
Dashboard: View overall statistics of the club, including total members, upcoming events, and pending approvals.

Event Management: Create, edit, and delete events.

Member Management: View, approve, and delete member requests.

Announcement Management: Create, edit, and delete announcements for different audiences.

Board of Directors (BOD)
Dashboard: View key metrics like member growth, event attendance, and donation summaries.

View Events: See a list of all club events.

View Members: Access a directory of all approved club members.

Donation Tracking: Monitor and search donation records.

Member
Dashboard: Personalized dashboard with an overview of attended events, and upcoming events.

Event Management: View and register for upcoming events.

Announcements: Stay updated with club news and announcements.

Profile Management: View and edit personal profile information.

Public
Homepage: A public-facing page showcasing the club's mission, featured events, and contact information.

Login/Register: Members and BOD can log in or register for an account.

Technologies Used
Backend: Flask (Python)

Frontend: HTML, Tailwind CSS, JavaScript

Database: In-memory data structures (with a setup file for SQLite)

Templating: Jinja2

File Structure
/
├── app.py
├── database_setup.py
├── README.md
├── static/
│   ├── style.css
│   └── uploads/
│       └── ... (event banners, etc.)
└── templates/
    ├── admin.html
    ├── admin_dashboard.html
    ├── announcement_form.html
    ├── announcements_list.html
    ├── base.html
    ├── bod.html
    ├── bod_base.html
    ├── bod_dashboard.html
    ├── bod_donations_list.html
    ├── bod_events_list.html
    ├── bod_members_list.html
    ├── dashboard.html
    ├── event_form.html
    ├── events_list.html
    ├── home.html
    ├── login.html
    ├── member.html
    ├── member_announcements.html
    ├── member_dashboard.html
    ├── member_events.html
    ├── member_profile.html
    ├── members_list.html
    └── register.html
Getting Started
Prerequisites
Python 3.x

Flask

Installation
Clone the repository:

Bash

git clone https://github.com/harshilahir1012/rotosite.git
cd rotosite
Create a virtual environment (recommended):

Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install the dependencies:

Bash

pip install Flask
Run the application:

Bash

python app.py
The application will be running at http://127.0.0.1:5000.

Usage
Admin: Login with username admin and password adminpass.

BOD: Login with username bod and password bodpass.

Member: Login with username member and password memberpass.

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.