import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
DATABASE_URL = os.getenv('DATABASE_URL')
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')
PORT = int(os.getenv('PORT', '8080'))

def get_db_config():
    if DATABASE_URL:
        parts = DATABASE_URL.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        return {
            'user': user_pass[0],
            'password': user_pass[1],
            'host': host_db[0].split('/')[0],
            'database': host_db[1].split('?')[0],
            'port': '5432'
        }
    return None

DB_CONFIG = get_db_config()

TOTAL_NUMERIC = 430
TOTAL_LETTER = 12

