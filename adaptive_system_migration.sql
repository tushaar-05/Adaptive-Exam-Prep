-- Adaptive Exam Prep System - Performance Tracking Tables

-- Table to track quiz attempts and scores
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    total_questions INT NOT NULL,
    time_taken INT NOT NULL, -- in minutes
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_subject (user_id, subject_name),
    INDEX idx_attempted_at (attempted_at)
);

-- Table to track study sessions
CREATE TABLE IF NOT EXISTS study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    duration INT NOT NULL, -- in minutes
    session_type ENUM('revision', 'practice', 'learning') DEFAULT 'learning',
    completed BOOLEAN DEFAULT FALSE,
    scheduled_at DATETIME NOT NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_scheduled (user_id, scheduled_at),
    INDEX idx_subject (subject_name)
);

-- Table to store adaptive recommendations
CREATE TABLE IF NOT EXISTS adaptive_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    recommendation_type ENUM('extra_practice', 'revision', 'time_management', 'confidence_mismatch') NOT NULL,
    priority ENUM('high', 'medium', 'low') DEFAULT 'medium',
    reason TEXT NOT NULL,
    action_plan TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_active (user_id, is_active)
);

-- Add performance tracking columns to user_subjects
ALTER TABLE user_subjects 
ADD COLUMN IF NOT EXISTS average_score DECIMAL(5,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_quizzes INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_quiz_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS performance_trend ENUM('improving', 'stable', 'declining') DEFAULT 'stable',
ADD COLUMN IF NOT EXISTS needs_attention BOOLEAN DEFAULT FALSE;

-- Insert sample quiz data for testing
INSERT INTO quiz_attempts (user_id, subject_name, score, total_questions, time_taken) VALUES
(1, 'Mathematics', 45.50, 20, 25),
(1, 'Mathematics', 50.00, 20, 22),
(1, 'Physics', 85.00, 20, 30),
(1, 'Chemistry', 90.00, 20, 28);
