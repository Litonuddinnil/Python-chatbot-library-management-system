import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# Gemini configuration (Optional fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# MongoDB configuration matching your Express Cluster0 setup
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://library-management:4reLpdGuZoUEQSpR@cluster0.jc89u.mongodb.net/?appName=Cluster0"
)
import os

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set")

DB_NAME = os.getenv("DB_NAME", "LibraryDB")

BooksCollection = "books"
UsersCollection = "users"
NotificationsCollection = "notifications"
SubmissionsCollection = "submissions"
FacultyNotesCollection = "faculty_notes"
reviewsCollection = "reviews"