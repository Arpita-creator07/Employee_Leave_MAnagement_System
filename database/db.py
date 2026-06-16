import pyodbc
import config

def get_connection():
    return pyodbc.connect(config.DB_CONNECTION)
