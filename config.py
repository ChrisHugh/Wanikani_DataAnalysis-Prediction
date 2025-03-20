import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
WANIKANI_API_KEY = os.getenv('WANIKANI_API_KEY')

if not WANIKANI_API_KEY:
    raise ValueError("Wanikani API key not found in environment variables. Please check the .env file.") 