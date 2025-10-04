import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'study_planner'
}

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def import_sample_quotes():
    """Import sample motivation quotes into the database"""
    
    sample_quotes = [
        {
            'quote_text': "Push yourself, because no one else is going to do it for you.",
            'author': "Unknown",
            'category': "Motivation"
        },
        {
            'quote_text': "The secret of getting ahead is getting started.",
            'author': "Mark Twain",
            'category': "Procrastination"
        },
        {
            'quote_text': "Don't limit your challenges. Challenge your limits.",
            'author': "Unknown",
            'category': "Growth"
        },
        {
            'quote_text': "The expert in anything was once a beginner.",
            'author': "Helen Hayes",
            'category': "Learning"
        },
        {
            'quote_text': "Success doesn't come from what you do occasionally, it comes from what you do consistently.",
            'author': "Marie Forleo",
            'category': "Consistency"
        },
        {
            'quote_text': "The harder you work for something, the greater you'll feel when you achieve it.",
            'author': "Unknown",
            'category': "Achievement"
        },
        {
            'quote_text': "Education is the most powerful weapon which you can use to change the world.",
            'author': "Nelson Mandela",
            'category': "Education"
        },
        {
            'quote_text': "Believe you can and you're halfway there.",
            'author': "Theodore Roosevelt",
            'category': "Belief"
        },
        {
            'quote_text': "Your future is created by what you do today, not tomorrow.",
            'author': "Robert Kiyosaki",
            'category': "Action"
        },
        {
            'quote_text': "The beautiful thing about learning is that no one can take it away from you.",
            'author': "B.B. King",
            'category': "Learning"
        }
    ]
    
    connection = get_db_connection()
    if connection is None:
        print("Failed to connect to database")
        return
    
    try:
        cursor = connection.cursor()
        
        # Clear existing quotes (optional)
        cursor.execute("DELETE FROM motivation_quotes")
        
        # Insert sample quotes
        insert_query = """
        INSERT INTO motivation_quotes (quote_text, author, category)
        VALUES (%s, %s, %s)
        """
        
        for quote in sample_quotes:
            cursor.execute(insert_query, (
                quote['quote_text'],
                quote['author'],
                quote['category']
            ))
        
        connection.commit()
        print(f"Successfully imported {len(sample_quotes)} quotes into the database")
        
    except Error as e:
        print(f"Error importing quotes: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    import_sample_quotes()