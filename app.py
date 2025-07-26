# app.py
# This is the merged file with user authentication, event management, and now member management.

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import datetime
import json
from collections import defaultdict

# --- Application Setup ---
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
# uri sqlite
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Custom Jinja filters
@app.template_filter('month_name')
def month_name(month_num):
    months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[month_num] if 1 <= month_num <= 12 else ''


# --- Databases (for Hackathon simplicity) ---

# Dummy users for login
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'member': {'password': 'memberpass', 'role': 'member'},
    'visitor': {'password': 'visitorpass', 'role': 'visitor'},
    'bod': {'password': 'bodpass', 'role': 'bod'},
}
roles = ['admin', 'member', 'visitor', 'bod']

# In-memory database for events
events_db = [
    {
        'id': 1,
        'title': 'Annual Blood Donation Camp',
        'description': 'Join us to save lives. Every drop counts!',
        'date': '2025-08-15',
        'time': '10:00',
        'location': 'LJIET College Campus',
        'banner': 'uploads/blood_donation_banner.png',
        'is_active': True,
        'attendance': 120 # New field
    },
    {
        'id': 2,
        'title': 'Tree Plantation Drive',
        'description': 'Let\'s make our world greener, one tree at a time.',
        'date': '2025-07-05', # Past event for summary
        'time': '09:00',
        'location': 'Riverfront Park',
        'banner': 'uploads/default_banner_2.jpg',
        'is_active': True,
        'attendance': 75 # New field
    }
]
next_event_id = 3

# ENHANCED: In-memory database for members with college-specific fields
members_db = [
    {
        'id': 1,
        'name': 'Priya Sharma',
        'email': 'priya.s@example.com',
        'join_date': '2025-07-20',
        'status': 'approved',
        'branch': 'Computer Engineering',
        'year': '3rd',
        'college_id': '22BECE101',
        'avatar': 'https://placehold.co/100x100/a0aec0/ffffff?text=PS'
    },
    {
        'id': 2,
        'name': 'Rohan Mehta',
        'email': 'rohan.m@example.com',
        'join_date': '2025-07-22',
        'status': 'approved',
        'branch': 'Mechanical Engineering',
        'year': '2nd',
        'college_id': '23BEME205',
        'avatar': 'https://placehold.co/100x100/4a5568/ffffff?text=RM'
    },
    {
        'id': 3,
        'name': 'Aarav Desai',
        'email': 'aarav.d@example.com',
        'join_date': '2025-06-24',
        'status': 'approved',
        'branch': 'Computer Engineering',
        'year': '1st',
        'college_id': '24BECE310',
        'avatar': 'https://placehold.co/100x100/9b2c2c/ffffff?text=AD'
    },
    {
        'id': 4,
        'name': 'Saanvi Patel',
        'email': 'saanvi.p@example.com',
        'join_date': '2025-07-25',
        'status': 'pending',
        'branch': 'IT Engineering',
        'year': '3rd',
        'college_id': '22BEIT115',
        'avatar': 'https://placehold.co/100x100/2c5282/ffffff?text=SP'
    }
]
next_member_id = 5

# In-memory database for announcements
announcements_db = [
    {
        'id': 1,
        'title': 'Welcome to the New Academic Year!',
        'content': 'A warm welcome to all new and returning members. We have an exciting year of events planned. Stay tuned!',
        'created_at': '2025-07-20 10:00:00',
        'created_by': 'admin',
        'expiry_date': '2025-08-30',
        'audience': ['All Members'],
        'attachment': None,
        'pinned': True,
        'status': 'published'
    }
]
next_announcement_id = 2

# ENHANCED: In-memory database for donations
donations_db = [
    {'id': 1, 'donor_name': 'Tech Solutions Inc.', 'amount': 5000, 'date': '2025-07-15', 'campaign': 'General Fund', 'transaction_id': 'TXN1001'},
    {'id': 2, 'donor_name': 'Alumni Association', 'amount': 7500, 'date': '2025-07-18', 'campaign': 'Blood Donation Camp', 'transaction_id': 'TXN1002'},
    {'id': 3, 'donor_name': 'Local Cafe', 'amount': 2500, 'date': '2025-07-20', 'campaign': 'General Fund', 'transaction_id': 'N/A (Cash)'},
    {'id': 4, 'donor_name': 'Dr. Anjali Verma', 'amount': 3000, 'date': '2025-07-22', 'campaign': 'Tree Plantation Drive', 'transaction_id': 'TXN1003'},
    {'id': 5, 'donor_name': 'Tech Solutions Inc.', 'amount': 2000, 'date': '2025-07-24', 'campaign': 'General Fund', 'transaction_id': 'TXN1004'},
]
next_donation_id = 6


# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_event_by_id(event_id):
    for event in events_db:
        if event['id'] == event_id: return event
    return None

def get_member_by_id(member_id):
    for member in members_db:
        if member['id'] == member_id: return member
    return None

def get_announcement_by_id(announcement_id):
    for announcement in announcements_db:
        if announcement['id'] == announcement_id: return announcement
    return None

def get_donation_by_id(donation_id):
    for donation in donations_db:
        if donation['id'] == donation_id: return donation
    return None
# --- User Authentication Routes ---

# Add these new routes and update existing ones in your app.py:

@app.route('/')
def home():
    """Public homepage for all visitors."""
    # Show only active upcoming events on homepage
    today = datetime.date.today()
    active_events = [
        event for event in events_db 
        if event['is_active'] and datetime.datetime.strptime(event['date'], '%Y-%m-%d').date() >= today
    ]
    # Limit to 3 most recent upcoming events for homepage
    active_events = sorted(active_events, key=lambda x: x['date'])[:3]
    
    # If user is already logged in, redirect to their dashboard
    if 'role' in session:
        if session['role'] == 'admin': 
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for(f"{session['role']}_dashboard"))
    
    return render_template('home.html', events=active_events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page - updated to remove visitor option from dropdown"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = users.get(username)
        if user and user['password'] == password and user['role'] == role:
            session['username'] = username
            session['role'] = role
            flash(f'Welcome, {username.capitalize()}!', 'success')
            if role == 'admin': 
                return redirect(url_for('admin_dashboard'))
            # Redirect other roles to their specific dashboards
            return redirect(url_for(f'{role}_dashboard'))
        else:
            flash('Invalid credentials or role!', 'error')
    
    # If already logged in, redirect to appropriate dashboard
    if 'role' in session:
        if session['role'] == 'admin': 
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for(f"{session['role']}_dashboard"))
        
    return render_template('login.html', roles=['admin', 'member', 'bod'])  # Removed 'visitor'

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page for BOD and Members"""
    global next_member_id
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        if username in users:
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        # Check if email already exists in members_db
        if any(member['email'] == email for member in members_db):
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        try:
            # Add to users database
            users[username] = {
                'password': password,
                'role': role,
                'email': email
            }
            
            # If registering as member, add to members_db with additional info
            if role == 'member':
                full_name = request.form.get('full_name', username)
                branch = request.form.get('branch', '')
                year = request.form.get('year', '')
                college_id = request.form.get('college_id', '')
                
                # Generate avatar placeholder
                initials = ''.join([name[0].upper() for name in full_name.split()[:2]])
                avatar_url = f'https://placehold.co/100x100/667eea/ffffff?text={initials}'
                
                new_member = {
                    'id': next_member_id,
                    'name': full_name,
                    'email': email,
                    'join_date': datetime.date.today().strftime('%Y-%m-%d'),
                    'status': 'pending',  # Requires admin approval
                    'branch': branch,
                    'year': year,
                    'college_id': college_id,
                    'avatar': avatar_url
                }
                
                members_db.append(new_member)
                next_member_id += 1
                
                flash('Registration successful! Your membership is pending approval from admin.', 'success')
            else:
                flash('Registration successful! You can now login.', 'success')
            
            return redirect(url_for('login'))
            
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')
@app.route('/logout')
def logout():
    # Clear session or user login info here
    session.clear()
    return redirect(url_for('login'))  # or your homepage

# --- Role Dashboards ---
@app.route('/member')
def member_dashboard():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    # Get member info from database
    username = session.get('username')
    member_info = None
    for member in members_db:
        if member['email'] == users.get(username, {}).get('email'):
            member_info = member
            break
    
    # Calculate member-specific stats
    today = datetime.date.today()
    upcoming_events = [e for e in events_db if e['is_active'] and datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() >= today]
    upcoming_events = sorted(upcoming_events, key=lambda x: x['date'])[:5]  # Next 5 events
    
    # Get recent announcements for members
    recent_announcements = [a for a in announcements_db if a['status'] == 'published' and 'All Members' in a['audience']]
    recent_announcements = sorted(recent_announcements, key=lambda x: x['created_at'], reverse=True)[:3]
    
    # Member activity stats (mock data for now)
    member_stats = {
        'events_attended': 8,
        'hours_volunteered': 24,
        'days_member': (datetime.date.today() - datetime.datetime.strptime(member_info['join_date'], '%Y-%m-%d').date()).days if member_info else 0,
        'upcoming_events': len(upcoming_events)
    }
    
    return render_template('member_dashboard.html', 
                         member_info=member_info,
                         upcoming_events=upcoming_events,
                         recent_announcements=recent_announcements,
                         stats=member_stats)

# --- MEMBER PANEL ROUTES ---
# Member Events Management
@app.route('/member/events')
def member_events():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    today = datetime.date.today()
    upcoming_events = [e for e in events_db if e['is_active'] and datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() >= today]
    past_events = [e for e in events_db if datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() < today]
    
    return render_template('member_events.html', 
                         upcoming_events=upcoming_events,
                         past_events=past_events)

@app.route('/member/events/view/<int:event_id>')
def member_view_event(event_id):
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    event = get_event_by_id(event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('member_events'))
    
    return render_template('member_event_detail.html', event=event)

@app.route('/member/events/register/<int:event_id>', methods=['POST'])
def member_register_event(event_id):
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    event = get_event_by_id(event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('member_events'))
    
    # Here you would add registration logic
    flash(f'Successfully registered for {event["title"]}!', 'success')
    return redirect(url_for('member_view_event', event_id=event_id))

# Member Announcements Management
@app.route('/member/announcements')
def member_announcements():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    announcements = [a for a in announcements_db if a['status'] == 'published' and 'All Members' in a['audience']]
    announcements = sorted(announcements, key=lambda x: (x['pinned'], x['created_at']), reverse=True)
    
    return render_template('member_announcements.html', announcements=announcements)

@app.route('/member/announcements/view/<int:announcement_id>')
def member_view_announcement(announcement_id):
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    announcement = get_announcement_by_id(announcement_id)
    if not announcement:
        flash('Announcement not found.', 'error')
        return redirect(url_for('member_announcements'))
    
    return render_template('member_announcement_detail.html', announcement=announcement)

# Member Profile Management
@app.route('/member/profile')
def member_profile():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    username = session.get('username')
    member_info = None
    for member in members_db:
        if member['email'] == users.get(username, {}).get('email'):
            member_info = member
            break
    
    return render_template('member_profile_view.html', member_info=member_info)

@app.route('/member/profile/edit', methods=['GET', 'POST'])
def member_edit_profile():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    username = session.get('username')
    member_info = None
    for member in members_db:
        if member['email'] == users.get(username, {}).get('email'):
            member_info = member
            break
    
    if request.method == 'POST':
        # Update member information
        member_info['name'] = request.form['name']
        member_info['branch'] = request.form['branch']
        member_info['year'] = request.form['year']
        member_info['college_id'] = request.form['college_id']
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('member_profile'))
    
    return render_template('member_edit_profile.html', member_info=member_info)

# Member Certificates
@app.route('/member/certificates')
def member_certificates():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    # Mock certificate data
    certificates = [
        {
            'id': 1,
            'title': 'Blood Donation Certificate',
            'issued_date': '2025-07-15',
            'event': 'Annual Blood Donation Camp',
            'status': 'issued'
        },
        {
            'id': 2,
            'title': 'Volunteer Certificate',
            'issued_date': '2025-06-20',
            'event': 'Tree Plantation Drive',
            'status': 'issued'
        }
    ]
    
    return render_template('member_certificates.html', certificates=certificates)

@app.route('/member/certificates/download/<int:certificate_id>')
def member_download_certificate(certificate_id):
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    # Mock download logic
    flash('Certificate download started!', 'success')
    return redirect(url_for('member_certificates'))

# Member Settings
@app.route('/member/settings')
def member_settings():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    return render_template('member_settings.html')

@app.route('/member/settings/change-password', methods=['POST'])
def member_change_password():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    username = session.get('username')
    user = users.get(username)
    
    if user['password'] != current_password:
        flash('Current password is incorrect!', 'error')
    elif new_password != confirm_password:
        flash('New passwords do not match!', 'error')
    elif len(new_password) < 6:
        flash('Password must be at least 6 characters long!', 'error')
    else:
        user['password'] = new_password
        flash('Password changed successfully!', 'success')
    
    return redirect(url_for('member_settings'))

# Member Activity/Statistics
@app.route('/member/activity')
def member_activity():
    if session.get('role') != 'member': return redirect(url_for('login'))
    
    username = session.get('username')
    member_info = None
    for member in members_db:
        if member['email'] == users.get(username, {}).get('email'):
            member_info = member
            break
    
    # Mock activity data
    activity_data = {
        'events_attended': 8,
        'hours_volunteered': 24,
        'certificates_earned': 2,
        'announcements_read': 15,
        'recent_activities': [
            {'type': 'event', 'title': 'Blood Donation Camp', 'date': '2025-07-15'},
            {'type': 'announcement', 'title': 'New Event Announcement', 'date': '2025-07-10'},
            {'type': 'certificate', 'title': 'Volunteer Certificate', 'date': '2025-06-20'}
        ]
    }
    
    return render_template('member_activity.html', member_info=member_info, activity_data=activity_data)

@app.route('/visitor')
def visitor_dashboard():
    if session.get('role') != 'visitor': return redirect(url_for('login'))
    return f"<h1>Welcome Visitor: {session.get('username')}</h1><a href='/logout'>Logout</a>"

@app.route('/bod/dashboard')
def bod_dashboard():
    if session.get('role') != 'bod': return redirect(url_for('login'))
    
    # --- Calculate Stats for BOD ---
    total_members = len([m for m in members_db if m['status'] == 'approved'])
    current_month = datetime.date.today().month
    new_members_this_month = len([m for m in members_db if m['status'] == 'approved' and datetime.datetime.strptime(m['join_date'], '%Y-%m-%d').month == current_month])
    today = datetime.date.today()
    upcoming_events_count = len([e for e in events_db if datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() >= today])
    total_donations_amount = sum(d['amount'] for d in donations_db)

    stats = {
        'total_members': total_members,
        'new_members_this_month': new_members_this_month,
        'upcoming_events': upcoming_events_count,
        'total_donations': f"{total_donations_amount:,}" # Format with commas
    }

    # --- Prepare Chart Data ---
    attendance_chart_data = {"labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"], "data": [89, 91, 90, 92, 94, 93, 80, 84]}
    member_growth_chart_data = {"labels": ["Feb", "Mar", "Apr", "May", "Jun", "Jul"], "data": [15, 18, 22, 25, 30, 32]}

    # NEW: Process donation data for pie chart
    donor_summary = defaultdict(float)
    for donation in donations_db:
        donor_summary[donation['donor_name']] += donation['amount']
    
    donation_chart_data = {
        "labels": list(donor_summary.keys()),
        "data": list(donor_summary.values())
    }

    # --- Quick Look-in Lists ---
    recent_announcements = sorted([a for a in announcements_db if a['status'] == 'published'], key=lambda x: x['created_at'], reverse=True)[:3]
    recent_events = sorted([e for e in events_db if datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() < today], key=lambda x: x['date'], reverse=True)[:3]

    return render_template('bod_dashboard.html', 
                           stats=stats, 
                           attendance_chart_data=json.dumps(attendance_chart_data),
                           member_growth_chart_data=json.dumps(member_growth_chart_data),
                           donation_chart_data=json.dumps(donation_chart_data), # Pass new chart data
                           recent_announcements=recent_announcements,
                           recent_events=recent_events)

# --- Admin Dashboard Route ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    stats = {
        'total_members': len(members_db),
        'pending_approvals': len([m for m in members_db if m['status'] == 'pending']),
        'upcoming_events': len([e for e in events_db if datetime.datetime.strptime(e['date'], '%Y-%m-%d').date() >= datetime.date.today()]),
        'total_bod': len([u for u, d in users.items() if d.get('role') in ['admin', 'bod']]),
        'total_donations': "15,250",
        'announcements_posted': len([a for a in announcements_db if a['status'] == 'published'])
    }
    chart_data = {"labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"], "data": [89, 91, 90, 92, 94, 93, 80, 84]}
    return render_template('dashboard.html', stats=stats, chart_data=json.dumps(chart_data))


# --- Admin Panel Routes (No changes needed below this line) ---
# ... (Event Management, Member Management, Announcement Management routes are unchanged) ...
@app.route('/admin/events')
def list_events():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    return render_template('events_list.html', events=events_db)

@app.route('/admin/events/new', methods=['GET', 'POST'])
def create_event():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    global next_event_id
    if request.method == 'POST':
        new_event = {
            'id': next_event_id, 'title': request.form['title'], 'description': request.form['description'],
            'date': request.form['date'], 'time': request.form['time'], 'location': request.form['location'],
            'is_active': 'is_active' in request.form, 'banner': None, 'attendance': 0
        }
        if 'banner' in request.files:
            file = request.files['banner']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"event_{new_event['id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_event['banner'] = os.path.join('uploads', filename)
        events_db.append(new_event)
        next_event_id += 1
        flash('Event created successfully!', 'success')
        return redirect(url_for('list_events'))
    return render_template('event_form.html', event=None, action_url=url_for('create_event'))

@app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    event = get_event_by_id(event_id)
    if not event:
        flash('Event not found.', 'error'); return redirect(url_for('list_events'))
    if request.method == 'POST':
        event['title'] = request.form['title']; event['description'] = request.form['description']
        event['date'] = request.form['date']; event['time'] = request.form['time']
        event['location'] = request.form['location']; event['is_active'] = 'is_active' in request.form
        if 'banner' in request.files:
            file = request.files['banner']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"event_{event['id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                event['banner'] = os.path.join('uploads', filename)
        flash('Event updated successfully!', 'success')
        return redirect(url_for('list_events'))
    return render_template('event_form.html', event=event, action_url=url_for('edit_event', event_id=event_id))

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    global events_db
    event = get_event_by_id(event_id)
    if event:
        events_db = [e for e in events_db if e['id'] != event_id]
        flash('Event deleted successfully!', 'success')
    else:
        flash('Event not found.', 'error')
    return redirect(url_for('list_events'))

@app.route('/admin/members')
def list_members():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').lower()
    filtered_members = members_db
    if status_filter == 'pending':
        filtered_members = [m for m in filtered_members if m['status'] == 'pending']
        active_tab = 'pending'
    else:
        active_tab = 'all'
    if search_query:
        filtered_members = [
            m for m in filtered_members 
            if search_query in m['name'].lower() 
            or search_query in m['branch'].lower()
            or search_query in m['college_id'].lower()
        ]
    return render_template(
        'members_list.html', members=filtered_members, active_tab=active_tab, 
        members_db=members_db, search_query=search_query
    )

@app.route('/admin/members/profile/<int:member_id>')
def view_member_profile(member_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    member = get_member_by_id(member_id)
    if not member:
        flash('Member not found.', 'error')
        return redirect(url_for('list_members'))
    return render_template('member_profile.html', member=member)

@app.route('/admin/members/approve/<int:member_id>', methods=['POST'])
def approve_member(member_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    member = get_member_by_id(member_id)
    if member:
        member['status'] = 'approved'
        flash(f"Member '{member['name']}' has been approved.", 'success')
    else:
        flash('Member not found.', 'error')
    return redirect(url_for('list_members', status='pending'))

@app.route('/admin/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    global members_db
    member = get_member_by_id(member_id)
    if member:
        members_db = [m for m in members_db if m['id'] != member_id]
        flash(f"Member '{member['name']}' has been deleted.", 'success')
    else:
        flash('Member not found.', 'error')
    return redirect(url_for('list_members'))

@app.route('/admin/announcements')
def list_announcements():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    sorted_announcements = sorted(announcements_db, key=lambda x: (x['pinned'], x['created_at']), reverse=True)
    return render_template('announcements_list.html', announcements=sorted_announcements)

@app.route('/admin/announcements/new', methods=['GET', 'POST'])
def create_announcement():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    global next_announcement_id
    if request.method == 'POST':
        new_announcement = {
            'id': next_announcement_id, 'title': request.form['title'], 'content': request.form['content'],
            'expiry_date': request.form.get('expiry_date') or None, 'audience': request.form.getlist('audience'),
            'pinned': 'pinned' in request.form, 'status': 'published' if 'publish' in request.form else 'draft',
            'created_by': session.get('username', 'Unknown Admin'), 'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'attachment': None
        }
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"announcement_{new_announcement['id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_announcement['attachment'] = os.path.join('uploads', filename)
        announcements_db.append(new_announcement)
        next_announcement_id += 1
        flash(f"Announcement '{new_announcement['title']}' was successfully created as a {new_announcement['status']}.", 'success')
        return redirect(url_for('list_announcements'))
    return render_template('announcement_form.html', form_action='Create', announcement=None)

@app.route('/admin/announcements/edit/<int:announcement_id>', methods=['GET', 'POST'])
def edit_announcement(announcement_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    announcement = get_announcement_by_id(announcement_id)
    if not announcement:
        flash('Announcement not found.', 'error'); return redirect(url_for('list_announcements'))
    if request.method == 'POST':
        announcement['title'] = request.form['title']; announcement['content'] = request.form['content']
        announcement['expiry_date'] = request.form.get('expiry_date') or None
        announcement['audience'] = request.form.getlist('audience'); announcement['pinned'] = 'pinned' in request.form
        announcement['status'] = 'published' if 'publish' in request.form else 'draft'
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"announcement_{announcement['id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                announcement['attachment'] = os.path.join('uploads', filename)
        flash(f"Announcement '{announcement['title']}' was successfully updated.", 'success')
        return redirect(url_for('list_announcements'))
    return render_template('announcement_form.html', form_action='Edit', announcement=announcement)

@app.route('/admin/announcements/delete/<int:announcement_id>', methods=['POST'])
def delete_announcement(announcement_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    global announcements_db
    announcement = get_announcement_by_id(announcement_id)
    if announcement:
        announcements_db = [a for a in announcements_db if a['id'] != announcement_id]
        flash(f"Announcement '{announcement['title']}' has been deleted.", 'success')
    else:
        flash('Announcement not found.', 'error')
    return redirect(url_for('list_announcements'))

# --- NEW: BOD Panel: Donation Tracking Route ---
# --- NEW: BOD View Routes ---
@app.route('/bod/events')
def bod_list_events():
    if session.get('role') != 'bod': return redirect(url_for('login'))
    return render_template('bod_events_list.html', events=events_db)

@app.route('/bod/members')
def bod_list_members():
    if session.get('role') != 'bod': return redirect(url_for('login'))
    approved_members = [m for m in members_db if m['status'] == 'approved']
    return render_template('bod_members_list.html', members=approved_members)

@app.route('/bod/donations')
def bod_list_donations():
    if session.get('role') != 'bod': return redirect(url_for('login'))
    search_query = request.args.get('search', '').lower()
    donations_to_show = donations_db
    if search_query:
        donations_to_show = [
            d for d in donations_db 
            if search_query in d['donor_name'].lower() 
            or search_query in d['campaign'].lower()
        ]
    return render_template('bod_donations_list.html', donations=donations_to_show, search_query=search_query)


# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
