-- Add Google OAuth columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) NULL,
ADD COLUMN IF NOT EXISTS google_access_token TEXT NULL,
ADD COLUMN IF NOT EXISTS google_refresh_token TEXT NULL,
ADD INDEX idx_google_id (google_id);

-- Make password nullable for Google OAuth users
ALTER TABLE users 
MODIFY COLUMN password VARCHAR(255) NULL;
