import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables.")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

# User limits
MAX_MEDICATIONS_PER_USER = 20
MAX_TIMES_PER_MEDICATION = 6