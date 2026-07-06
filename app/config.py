import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY  = os.getenv('SECRET_KEY', 'forensic-mis-dev-key-2024')
    DB_HOST     = os.getenv('DB_HOST', 'localhost')
    DB_PORT     = int(os.getenv('DB_PORT', 5432))
    DB_NAME     = os.getenv('DB_NAME', 'forensic_db')
    DB_USER     = os.getenv('DB_USER', 'postgres')
    # ── IMPORTANT: put your actual postgres password below ──
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
