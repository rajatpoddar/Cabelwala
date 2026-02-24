# Cabelwala - ISP & CCTV Management System

## Overview
Cabelwala is a comprehensive billing, invoice generation, and business management platform designed specifically for Internet Service Providers (ISPs) and CCTV Installation businesses. 

## Features
* **Professional Dashboard**: Track total clients, active fiber connections, and revenue.
* **Client Management**: Store client details, contact information, and service types.
* **Dynamic Invoice Generation**:
    * Create multi-item bills with automated total calculations.
    * Special features for "Internet Recharge" (auto-calculates months between dates).
    * Generates professional PDF invoices.
    * Dynamic UPI QR Code embedding for instant payments.
* **Public Landing Page**: Showcase your business, YouTube portfolio, and accept new service requests directly via WhatsApp.
* **Mobile-Friendly Admin Panel**: Fully responsive sidebar and interfaces for managing the business on the go.

## Tech Stack
* **Backend**: Python, Flask, Flask-SQLAlchemy
* **Database**: SQLite (Production-ready for PostgreSQL)
* **Frontend**: HTML5, Tailwind CSS, FontAwesome
* **PDF Generation**: WeasyPrint
* **QR Code**: `qrcode[pil]`

## Setup & Installation

1.  **Clone the Repository**
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application**:
    ```bash
    python app.py
    ```
5.  **Default Admin Credentials**:
    * Username: `admin`
    * Password: `password123`