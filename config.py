import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

DATABASE_PATH = os.getenv(
    'DATABASE_PATH',
    os.path.join(BASE_DIR, 'database', 'employee_leave_management.db')
)
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
