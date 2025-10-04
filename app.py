from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime, timedelta
from flask import session
import random
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

# OAuth 2.0 scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar'
]

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'study_planner')
}



def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        grade = request.form.get('grade')
        stream = request.form.get('stream')
        study_time = request.form.get('studyTime')
        hobbies = request.form.get('hobbies')
        subjects_json = request.form.get('subjects')
        
        # Handle exams (checkboxes - can be multiple)
        exams = request.form.getlist('exams')
        
        # Convert exams list to JSON string for storage
        exams_json = json.dumps(exams) if exams else None
        
        # Parse subjects JSON
        subjects = json.loads(subjects_json) if subjects_json else {}
        
        # Validate required fields
        if not all([name, email, password, grade, study_time]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        # Validate stream for 11th/12th grade
        if grade in ['11', '12'] and not stream:
            return jsonify({'error': 'Stream is required for 11th and 12th grade'}), 400
        
        # Validate subjects
        if not subjects:
            return jsonify({'error': 'Please rate your confidence levels for all subjects'}), 400
        
        # Create database connection
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'Email already exists'}), 400
        
        # Insert new user
        insert_user_query = """
        INSERT INTO users (name, email, password, grade, stream, study_time, hobbies, exams)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_user_query, (name, email, password, grade, stream, study_time, hobbies, exams_json))
        connection.commit()
        
        # Get the inserted user ID
        user_id = cursor.lastrowid
        
        # Insert subjects into user_subjects table
        insert_subject_query = """
        INSERT INTO user_subjects (user_id, subject_name, confidence_level)
        VALUES (%s, %s, %s)
        """
        
        for subject_name, confidence_level in subjects.items():
            cursor.execute(insert_subject_query, (user_id, subject_name, confidence_level))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Welcome to Student Study Planner 🎉',
            'user_id': user_id
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/users')
def view_users():
    """Route to view all users (for testing purposes)"""
    try:
        connection = get_db_connection()
        if connection is None:
            return "Database connection failed"
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.grade, u.stream, u.study_time, u.hobbies, u.exams, u.created_at,
                   GROUP_CONCAT(CONCAT(us.subject_name, ' (', us.confidence_level, ')') SEPARATOR ', ') as subjects
            FROM users u
            LEFT JOIN user_subjects us ON u.id = us.user_id
            GROUP BY u.id
        """)
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('users.html', users=users)
        
    except Error as e:
        return f"Database error: {e}"

@app.route('/user/<int:user_id>/subjects')
def view_user_subjects(user_id):
    """Route to view specific user's subjects"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute("SELECT id, name, email, grade, stream FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get user subjects
        cursor.execute("""
            SELECT subject_name, confidence_level, created_at 
            FROM user_subjects 
            WHERE user_id = %s 
            ORDER BY subject_name
        """, (user_id,))
        subjects = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'user': user,
            'subjects': subjects
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500

# Google OAuth Routes
@app.route('/auth/google/login')
def google_login():
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return jsonify({'error': 'Google OAuth not configured. Please set up credentials.'}), 500
    
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return jsonify({'error': 'Failed to initiate Google login'}), 500

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        if 'oauth_state' not in session:
            return redirect('/login?error=invalid_state')
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            state=session['oauth_state']
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Get authorization response
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get credentials
        credentials = flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('id')
        
        # Check if user exists
        connection = get_db_connection()
        if connection is None:
            return redirect('/login?error=db_connection')
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Update Google credentials
            cursor.execute("""
                UPDATE users 
                SET google_id = %s, google_access_token = %s, google_refresh_token = %s
                WHERE id = %s
            """, (google_id, credentials.token, credentials.refresh_token, user['id']))
            connection.commit()
            
            # Set session
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            session['user_grade'] = user['grade']
            session['user_stream'] = user['stream']
            session['google_credentials'] = credentials_to_dict(credentials)
            
            cursor.close()
            connection.close()
            return redirect('/dashboard')
        else:
            # New user - redirect to complete signup
            session['google_user_info'] = {
                'email': email,
                'name': name,
                'google_id': google_id,
                'credentials': credentials_to_dict(credentials)
            }
            cursor.close()
            connection.close()
            return redirect('/create?google=true')
            
    except Exception as e:
        print(f"Google callback error: {e}")
        return redirect('/login?error=oauth_failed')

def credentials_to_dict(credentials):
    """Convert credentials object to dictionary"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# API endpoint for Google signup (placeholder)
@app.route('/api/google-signup', methods=['POST'])
def google_signup():
    """Initiate Google OAuth for signup"""
    return redirect('/auth/google/login')

# Add login route
@app.route('/login', methods=['POST'])
def login():
    try:
        # Get form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Validate required fields
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Create database connection
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid email address'}), 401
        
        # Check password (in production, use proper password hashing!)
        if user['password'] != password:  # Replace with proper password verification
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid password'}), 401
        
        # Get user subjects for session
        cursor.execute("""
            SELECT subject_name, confidence_level 
            FROM user_subjects 
            WHERE user_id = %s
        """, (user['id'],))
        subjects = cursor.fetchall()
        
        # Convert subjects to dictionary for easy access
        subjects_dict = {subject['subject_name']: subject['confidence_level'] for subject in subjects}
        
        # Set session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['user_grade'] = user['grade']
        session['user_stream'] = user['stream']
        session['user_subjects'] = subjects_dict
        
        # Set session permanence based on remember me
        if remember:
            session.permanent = True
        else:
            session.permanent = False
        
        cursor.close()
        connection.close()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Login successful! Welcome back! 🎉',
            'redirect_url': '/dashboard',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'grade': user['grade'],
                'stream': user['stream'],
                'subjects': subjects_dict
            }
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Add login page route
@app.route('/login')
def login_page():
    return render_template('login.html')

# Add logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Google login API endpoint
@app.route('/api/google-login', methods=['POST'])
def google_login_api():
    """API endpoint to redirect to Google OAuth"""
    return jsonify({
        'redirect_url': '/auth/google/login'
    })

# Google Calendar Integration
def get_calendar_service(user_id):
    """Get Google Calendar service for a user"""
    try:
        connection = get_db_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT google_access_token, google_refresh_token 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user or not user.get('google_access_token'):
            return None
        
        credentials = Credentials(
            token=user['google_access_token'],
            refresh_token=user['google_refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error getting calendar service: {e}")
        return None

@app.route('/api/calendar/events')
def get_calendar_events():
    """Get user's calendar events"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        service = get_calendar_service(session['user_id'])
        if not service:
            return jsonify({'error': 'Google Calendar not connected', 'connected': False}), 200
        
        # Get events for the next 30 days
        now = datetime.utcnow().isoformat() + 'Z'
        end_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_date,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        return jsonify({
            'success': True,
            'connected': True,
            'events': events
        })
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return jsonify({'error': 'Failed to fetch calendar events', 'connected': False}), 500

@app.route('/api/calendar/create-event', methods=['POST'])
def create_calendar_event():
    """Create a new calendar event"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        service = get_calendar_service(session['user_id'])
        if not service:
            return jsonify({'error': 'Google Calendar not connected'}), 400
        
        data = request.json
        event = {
            'summary': data.get('title'),
            'description': data.get('description', ''),
            'start': {
                'dateTime': data.get('start_time'),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': data.get('end_time'),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': created_event
        })
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return jsonify({'error': 'Failed to create calendar event'}), 500

# Forgot password route (placeholder)
@app.route('/forgot-password')
def forgot_password():
    return "Forgot password page - to be implemented"

# Add this function to get a random quote
def get_random_quote():
    """Get a random active quote from the database"""
    try:
        connection = get_db_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT quote_text, author, category 
            FROM motivation_quotes 
            WHERE is_active = TRUE 
            ORDER BY RAND() 
            LIMIT 1
        """)
        quote = cursor.fetchone()
        
        cursor.close()
        connection.close()
        return quote
        
    except Error as e:
        print(f"Error fetching quote: {e}")
        return None


# Update your dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get a random quote for the dashboard
    quote = get_random_quote()
    
    # You can pass user data and quote to the template
    return render_template('dashboard.html', quote=quote)

# API endpoint to get a new random quote
@app.route('/api/random-quote')
def random_quote():
    quote = get_random_quote()
    if quote:
        return jsonify({
            'success': True,
            'quote': quote
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No quotes available'
        }), 404

# Get all quotes (for admin purposes)
@app.route('/api/quotes')
def get_all_quotes():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, quote_text, author, category, created_at, is_active 
            FROM motivation_quotes 
            ORDER BY created_at DESC
        """)
        quotes = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'quotes': quotes
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500

# Add new quote
@app.route('/api/quotes', methods=['POST'])
def add_quote():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.json
        quote_text = data.get('quote_text')
        author = data.get('author', 'Unknown')
        category = data.get('category', 'Motivation')
        
        if not quote_text:
            return jsonify({'error': 'Quote text is required'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO motivation_quotes (quote_text, author, category)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(insert_query, (quote_text, author, category))
        connection.commit()
        
        quote_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Quote added successfully',
            'quote_id': quote_id
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# API to update user subjects
@app.route('/api/update-subjects', methods=['POST'])
def update_subjects():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        user_id = session['user_id']
        subjects_json = request.json.get('subjects')
        
        if not subjects_json:
            return jsonify({'error': 'No subjects provided'}), 400
        
        subjects = json.loads(subjects_json)
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Delete existing subjects
        cursor.execute("DELETE FROM user_subjects WHERE user_id = %s", (user_id,))
        
        # Insert new subjects
        insert_subject_query = """
        INSERT INTO user_subjects (user_id, subject_name, confidence_level)
        VALUES (%s, %s, %s)
        """
        
        for subject_name, confidence_level in subjects.items():
            cursor.execute(insert_subject_query, (user_id, subject_name, confidence_level))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Update session
        session['user_subjects'] = subjects
        
        return jsonify({
            'success': True,
            'message': 'Subjects updated successfully'
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# API to get user subjects
@app.route('/api/user-subjects')
def get_user_subjects():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        user_id = session['user_id']
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT subject_name, confidence_level 
            FROM user_subjects 
            WHERE user_id = %s 
            ORDER BY subject_name
        """, (user_id,))
        subjects = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'subjects': subjects
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)