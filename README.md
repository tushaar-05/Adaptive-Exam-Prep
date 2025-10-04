# Adaptive Exam Prep - Study Planner with Google Integration

A professional adaptive exam preparation platform with Google OAuth authentication and Google Calendar integration.

## Features

- ✨ **Professional UI/UX** - Modern, clean design with smooth animations
- 🔐 **Google OAuth Authentication** - Secure login with Google accounts
- 📅 **Google Calendar Integration** - Sync study events with Google Calendar
- 📊 **Personalized Study Plans** - Adaptive learning based on confidence levels
- 💡 **Motivational Quotes** - Daily inspiration for students
- 📈 **Progress Tracking** - Monitor study streaks and quiz performance
- 🎯 **Subject Management** - Track confidence levels across subjects

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Google OAuth 2.0, Google Calendar API
- **Icons**: Font Awesome

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL Server (XAMPP or standalone)
- Google Cloud Console account

### 2. Database Setup

1. Start your MySQL server (XAMPP or standalone)
2. Create the database:
```sql
CREATE DATABASE study_planner;
USE study_planner;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NULL,
    grade VARCHAR(10) NOT NULL,
    stream VARCHAR(50) NULL,
    study_time DECIMAL(3,1) NOT NULL,
    hobbies TEXT NULL,
    exams JSON NULL,
    google_id VARCHAR(255) NULL,
    google_access_token TEXT NULL,
    google_refresh_token TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_google_id (google_id)
);

-- Create user_subjects table
CREATE TABLE user_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    confidence_level INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create motivation_quotes table
CREATE TABLE motivation_quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author VARCHAR(255) DEFAULT 'Unknown',
    category VARCHAR(50) DEFAULT 'Motivation',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample quotes
INSERT INTO motivation_quotes (quote_text, author, category) VALUES
('Success is not final, failure is not fatal: it is the courage to continue that counts.', 'Winston Churchill', 'Motivation'),
('The only way to do great work is to love what you do.', 'Steve Jobs', 'Success'),
('Believe you can and you are halfway there.', 'Theodore Roosevelt', 'Confidence'),
('Education is the most powerful weapon which you can use to change the world.', 'Nelson Mandela', 'Education'),
('The future belongs to those who believe in the beauty of their dreams.', 'Eleanor Roosevelt', 'Dreams');
```

### 3. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Calendar API
   - Google+ API (for OAuth)
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure OAuth consent screen:
   - User Type: External
   - Add scopes: email, profile, calendar
6. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5000/auth/google/callback`
7. Download the credentials (you'll get Client ID and Client Secret)

### 4. Environment Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Flask Secret Key
SECRET_KEY=your_random_secret_key_here

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=study_planner
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### For Students

1. **Sign Up**: Create an account using email or Google OAuth
2. **Set Profile**: Select grade, stream, and rate confidence levels
3. **Dashboard**: View motivational quotes, study stats, and calendar
4. **Google Calendar**: 
   - Connect your Google account to sync events
   - Add study sessions directly to your calendar
   - View upcoming study events

### Google Calendar Features

- **Sync Events**: View your Google Calendar events in the dashboard
- **Create Events**: Add study sessions with reminders
- **Auto-sync**: Calendar updates automatically
- **Reminders**: Get notifications 30 and 10 minutes before events

## Project Structure

```
Adaptive-Exam-Prep/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── database_migration.sql # Database schema updates
├── README.md              # This file
├── static/
│   ├── css/
│   │   └── signup.css
│   ├── images/
│   │   ├── login.jpg
│   │   └── signup.jpg
│   └── js/
│       └── signup.js
└── templates/
    ├── index.html         # Landing page
    ├── login.html         # Login page
    ├── signup.html        # Registration page
    ├── dashboard.html     # Main dashboard
    ├── timetable.html     # Timetable view
    └── users.html         # User management
```

## Security Notes

- Never commit `.env` file to version control
- Keep your Google OAuth credentials secure
- Use HTTPS in production
- Implement proper password hashing (bcrypt recommended)
- Add CSRF protection for production use

## Future Enhancements

- [ ] AI-powered quiz generation
- [ ] Spaced repetition flashcards
- [ ] Study analytics and insights
- [ ] Mobile app integration
- [ ] Collaborative study groups
- [ ] Video conferencing integration

## Troubleshooting

### Google OAuth Issues

1. **Redirect URI mismatch**: Ensure the redirect URI in Google Console matches exactly
2. **Scope errors**: Make sure all required scopes are enabled
3. **Token expired**: The app will automatically refresh tokens

### Database Connection Issues

1. Check if MySQL server is running
2. Verify database credentials in `.env`
3. Ensure database and tables are created

### Calendar Not Syncing

1. Check if Google Calendar API is enabled
2. Verify OAuth scopes include calendar access
3. Re-authenticate with Google if needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
