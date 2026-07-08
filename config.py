import os
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# Gemini configuration (Optional fallback)
DeepSeek_Api_KEY = os.getenv("DeepSeek_Api_KEY", "YOUR_API_KEY_HERE")

# MongoDB configuration matching your Express Cluster0 setup
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://library-management:4reLpdGuZoUEQSpR@cluster0.jc89u.mongodb.net/?appName=Cluster0"
)

DB_NAME = os.getenv("DB_NAME", "LibraryDB")

# Collections
BooksCollection = "books"
UsersCollection = "users"
NotificationsCollection = "notifications"
SubmissionsCollection = "submissions"
FacultyNotesCollection = "faculty_notes"
reviewsCollection = "reviews"
