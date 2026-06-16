import os
import pyodbc
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH, override=True)
DEFAULT_DB_CONNECTION = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\\MSSQLLocalDB;DATABASE=EmployeeLeaveManagementSystem;Trusted_Connection=yes;Encrypt=no;'


def _pick_sql_server_driver(configured_driver: str) -> str:
    available_drivers = {driver.upper(): driver for driver in pyodbc.drivers()}
    cleaned_driver = (configured_driver or '').strip()

    if cleaned_driver:
        normalized = cleaned_driver.strip('{}').upper()
        for candidate_upper, candidate in available_drivers.items():
            if candidate_upper == normalized:
                return candidate

    for preferred in ('ODBC Driver 18 for SQL Server', 'ODBC Driver 17 for SQL Server', 'SQL Server'):
        if preferred.upper() in available_drivers:
            return available_drivers[preferred.upper()]

    return cleaned_driver.strip('{}') or 'ODBC Driver 17 for SQL Server'


def _build_connection_from_parts() -> str:
    driver = _pick_sql_server_driver(os.getenv('DRIVER', ''))
    server = os.getenv('SERVER', '(localdb)\\MSSQLLocalDB').strip()
    database = os.getenv('DATABASE', 'EmployeeLeaveManagementSystem').strip()
    trusted_connection = os.getenv('Trusted_Connection', 'yes').strip()
    encrypt = os.getenv('Encrypt', 'no').strip()
    trust_server_certificate = os.getenv('TrustServerCertificate', 'yes').strip()

    parts = [
        f'DRIVER={{{driver}}}',
        f'SERVER={server}',
        f'DATABASE={database}',
        f'Trusted_Connection={trusted_connection}',
        f'Encrypt={encrypt}',
        f'TrustServerCertificate={trust_server_certificate}',
    ]

    uid = os.getenv('UID', '').strip()
    pwd = os.getenv('PWD', '').strip()
    if uid:
        parts.append(f'UID={uid}')
    if pwd:
        parts.append(f'PWD={pwd}')

    return ';'.join(parts) + ';'


def _normalize_connection_string(raw_value: str) -> str:
    value = (raw_value or '').strip().strip("'").strip('"')
    value = value.replace('\r', '').replace('\n', '')
    if not value:
        return _build_connection_from_parts()

    upper = value.upper()
    if 'SERVER=' not in upper and 'DSN=' not in upper:
        return _build_connection_from_parts()

    return value


DB_CONNECTION = _normalize_connection_string(os.getenv('DB_CONNECTION', ''))
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
