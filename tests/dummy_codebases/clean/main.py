import os

def db_connect(host):
    return "connected"

def run_app():
    host = os.getenv('DB_HOST', 'localhost')
    password = os.getenv('PASS')
    db = db_connect(host)
    return True
