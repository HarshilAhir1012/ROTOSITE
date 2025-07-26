# import sqlite3
# import hashlib

# # --- Hashing function for passwords ---
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # --- Connect to (or create) the database file ---
# conn = sqlite3.connect('rotaract.db')
# cursor = conn.cursor()

# # --- Create Tables (with IF NOT EXISTS to be safe) ---

# # Users Table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT NOT NULL UNIQUE,
#     password TEXT NOT NULL,
#     role TEXT NOT NULL
# )
# ''')

# # Events Table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS events (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     description TEXT,
#     date TEXT,
#     time TEXT,
#     location TEXT,
#     banner TEXT,
#     is_active BOOLEAN,
#     attendance INTEGER DEFAULT 0
# )
# ''')

# # Members Table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS members (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     email TEXT UNIQUE,
#     join_date TEXT,
#     status TEXT,
#     branch TEXT,
#     year TEXT,
#     college_id TEXT,
#     avatar TEXT
# )
# ''')

# # Announcements Table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS announcements (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     content TEXT,
#     created_at TEXT,
#     created_by TEXT,
#     expiry_date TEXT,
#     audience TEXT,
#     attachment TEXT,
#     pinned BOOLEAN,
#     status TEXT
# )
# ''')

# # Donations Table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS donations (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     donor_name TEXT NOT NULL,
#     amount REAL,
#     date TEXT,
#     campaign TEXT,
#     transaction_id TEXT
# )
# ''')

# print("Tables created successfully (if they didn't already exist).")


# # --- Populate Tables with Initial Data ---

# # Clear existing data to avoid duplicates on re-run
# cursor.execute("DELETE FROM users")
# cursor.execute("DELETE FROM events")
# cursor.execute("DELETE FROM members")
# cursor.execute("DELETE FROM announcements")
# cursor.execute("DELETE FROM donations")
# print("Cleared existing data from tables.")

# # Insert Users (with hashed passwords)
# users_to_insert = [
#     ('admin', hash_password('adminpass'), 'admin'),
#     ('member', hash_password('memberpass'), 'member'),
#     ('visitor', hash_password('visitorpass'), 'visitor'),
#     ('bod', hash_password('bodpass'), 'bod')
# ]
# cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users_to_insert)

# # Insert Events
# events_to_insert = [
#     ('Annual Blood Donation Camp', 'Join us to save lives. Every drop counts!', '2025-08-15', '10:00', 'LJIET College Campus', 'uploads/blood_donation_banner.png', True, 120),
#     ('Tree Plantation Drive', "Let's make our world greener, one tree at a time.", '2025-07-05', '09:00', 'Riverfront Park', 'uploads/default_banner_2.jpg', True, 75)
# ]
# cursor.executemany("INSERT INTO events (title, description, date, time, location, banner, is_active, attendance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", events_to_insert)

# # Insert Members
# members_to_insert = [
#     ('Priya Sharma', 'priya.s@example.com', '2025-07-20', 'approved', 'Computer Engineering', '3rd', '22BECE101', 'https://placehold.co/100x100/a0aec0/ffffff?text=PS'),
#     ('Rohan Mehta', 'rohan.m@example.com', '2025-07-22', 'approved', 'Mechanical Engineering', '2nd', '23BEME205', 'https://placehold.co/100x100/4a5568/ffffff?text=RM'),
#     ('Aarav Desai', 'aarav.d@example.com', '2025-06-24', 'approved', 'Computer Engineering', '1st', '24BECE310', 'https://placehold.co/100x100/9b2c2c/ffffff?text=AD'),
#     ('Saanvi Patel', 'saanvi.p@example.com', '2025-07-25', 'pending', 'IT Engineering', '3rd', '22BEIT115', 'https://placehold.co/100x100/2c5282/ffffff?text=SP')
# ]
# cursor.executemany("INSERT INTO members (name, email, join_date, status, branch, year, college_id, avatar) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", members_to_insert)

# # Insert Announcements
# announcements_to_insert = [
#     ('Welcome to the New Academic Year!', 'A warm welcome to all new and returning members.', '2025-07-20 10:00:00', 'admin', '2025-08-30', 'All Members', None, True, 'published')
# ]
# # For audience, we store a comma-separated string
# cursor.execute("INSERT INTO announcements (title, content, created_at, created_by, expiry_date, audience, attachment, pinned, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", announcements_to_insert[0])

# # Insert Donations
# donations_to_insert = [
#     ('Tech Solutions Inc.', 5000, '2025-07-15', 'General Fund', 'TXN1001'),
#     ('Alumni Association', 7500, '2025-07-18', 'Blood Donation Camp', 'TXN1002')
# ]
# cursor.executemany("INSERT INTO donations (donor_name, amount, date, campaign, transaction_id) VALUES (?, ?, ?, ?, ?)", donations_to_insert)


# # --- Commit changes and close the connection ---
# conn.commit()
# conn.close()

# print("Database `rotaract.db` has been created and populated with initial data.")
