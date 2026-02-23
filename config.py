import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-production-key'
    
    # Database: Defaults to SQLite, ready for PostgreSQL via environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'isp_cctv.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Storage
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    INVOICE_FOLDER = os.path.join(BASE_DIR, 'invoices')
    
    # Business Details
    BUSINESS_NAME = "CABELWALA"
    BUSINESS_TAGLINE = "Internet & CCTV Solutions"
    BUSINESS_PHONE = "+91-XXXXXXXXXX"
    
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(INVOICE_FOLDER, exist_ok=True)