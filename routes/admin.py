from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, Admin, Client, Invoice, InvoiceItem, BusinessProfile, Plan, Project, ServiceRequest
from datetime import datetime
import os
from weasyprint import HTML
import qrcode
import base64
from io import BytesIO

admin_bp = Blueprint('admin', __name__)

def generate_invoice_number():
    year = datetime.now().year
    prefix = f"ISP-{year}-"
    last_invoice = Invoice.query.filter(Invoice.invoice_number.like(f"{prefix}%")).order_by(Invoice.id.desc()).first()
    
    if last_invoice:
        last_seq = int(last_invoice.invoice_number.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
        
    return f"{prefix}{new_seq:04d}"

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Admin.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    total_clients = Client.query.count()
    active_fiber = Client.query.filter_by(service_type='Fiber').count()
    pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
    
    paid_invoices = Invoice.query.filter_by(status='Paid').all()
    total_revenue = sum(inv.total for inv in paid_invoices)
    
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_clients=total_clients, 
                           active_fiber=active_fiber,
                           pending_requests=pending_requests,
                           total_revenue=total_revenue,
                           recent_invoices=recent_invoices)

@admin_bp.route('/invoices')
@login_required
def invoices():
    all_invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('admin/invoices.html', invoices=all_invoices)

# Naya Route - Status Toggle ke liye
@admin_bp.route('/invoice/<int:invoice_id>/toggle_status', methods=['POST'])
@login_required
def toggle_invoice_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.status == 'Paid':
        invoice.status = 'Unpaid'
    else:
        invoice.status = 'Paid'
    db.session.commit()
    flash(f'Invoice #{invoice.invoice_number} marked as {invoice.status}', 'success')
    return redirect(url_for('admin.invoices'))

@admin_bp.route('/invoice/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        bill_for = request.form.get('bill_for')
        tax = float(request.form.get('tax', 0))
        status = request.form.get('status', 'Unpaid')
        
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        inv_number = generate_invoice_number()
        
        subtotal = 0
        new_invoice = Invoice(
            invoice_number=inv_number, client_id=client_id, bill_for=bill_for,
            subtotal=0, tax=tax, total=0, status=status
        )
        db.session.add(new_invoice)
        db.session.flush()
        
        for i in range(len(descriptions)):
            desc = descriptions[i]
            qty = int(quantities[i]) if quantities[i] else 1
            price = float(prices[i]) if prices[i] else 0.0
            item_total = qty * price
            subtotal += item_total
            
            item = InvoiceItem(
                invoice_id=new_invoice.id, description=desc, 
                quantity=qty, price=price, total=item_total
            )
            db.session.add(item)
            
        new_invoice.subtotal = subtotal
        new_invoice.total = subtotal + tax
        db.session.commit()
        
        logo_base64 = None
        logo_path = os.path.join(current_app.config.get('BASE_DIR', os.getcwd()), 'static', 'logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        
        business = BusinessProfile.query.first() or BusinessProfile()
        qr_base64 = None
        if business.upi_id:
            payee = business.payee_name or business.company_name
            upi_url = f"upi://pay?pa={business.upi_id}&pn={payee}&am={new_invoice.total}&cu=INR"
            qr = qrcode.QRCode(version=1, box_size=4, border=1)
            qr.add_data(upi_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            from io import BytesIO
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
        client = Client.query.get(client_id)
        rendered_html = render_template('admin/invoice_pdf.html', invoice=new_invoice, client=client, business=business, qr_code_data=qr_base64, logo_base64=logo_base64)
        
        pdf_filename = f"{inv_number}.pdf"
        pdf_path = os.path.join(current_app.config['INVOICE_FOLDER'], pdf_filename)
        HTML(string=rendered_html).write_pdf(pdf_path)
        
        new_invoice.pdf_filename = pdf_filename
        db.session.commit()
        
        flash('Bill Generated & PDF Saved Successfully!', 'success')
        return redirect(url_for('admin.invoices'))
        
    clients = Client.query.order_by(Client.name).all()
    plans = Plan.query.order_by(Plan.name).all()
    return render_template('admin/create_invoice.html', clients=clients, plans=plans)

@admin_bp.route('/invoice/download/<filename>')
@login_required
def download_invoice(filename):
    return send_from_directory(current_app.config['INVOICE_FOLDER'], filename, as_attachment=True)

@admin_bp.route('/clients', methods=['GET', 'POST'])
@login_required
def clients():
    if request.method == 'POST':
        new_client = Client(
            name=request.form.get('name'),
            mobile=request.form.get('mobile'),
            alt_mobile=request.form.get('alt_mobile'),
            address=request.form.get('address'),
            area=request.form.get('area'),
            service_type=request.form.get('service_type'),
            notes=request.form.get('notes')
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully!', 'success')
        return redirect(url_for('admin.clients'))
        
    all_clients = Client.query.order_by(Client.created_at.desc()).all()
    return render_template('admin/clients.html', clients=all_clients)

@admin_bp.route('/plans', methods=['GET', 'POST'])
@login_required
def plans():
    if request.method == 'POST':
        new_plan = Plan(
            name=request.form.get('name'),
            price=float(request.form.get('price'))
        )
        db.session.add(new_plan)
        db.session.commit()
        flash('Plan added successfully!', 'success')
        return redirect(url_for('admin.plans'))
    all_plans = Plan.query.all()
    return render_template('admin/plans.html', plans=all_plans)

# Service Requests Route
@admin_bp.route('/requests', methods=['GET'])
@login_required
def service_requests():
    requests_list = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).all()
    return render_template('admin/requests.html', requests=requests_list)

@admin_bp.route('/requests/<int:req_id>/complete', methods=['POST'])
@login_required
def complete_request(req_id):
    req = ServiceRequest.query.get_or_404(req_id)
    req.status = 'Completed'
    db.session.commit()
    flash('Request marked as completed!', 'success')
    return redirect(url_for('admin.service_requests'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile = BusinessProfile.query.first()
    if not profile:
        profile = BusinessProfile()
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.company_name = request.form.get('company_name')
        profile.phone = request.form.get('phone')
        profile.email = request.form.get('email')
        profile.address = request.form.get('address')
        profile.gst_no = request.form.get('gst_no')
        profile.bank_name = request.form.get('bank_name')
        profile.account_name = request.form.get('account_name')
        profile.account_number = request.form.get('account_number')
        profile.ifsc_code = request.form.get('ifsc_code')
        profile.branch = request.form.get('branch')
        profile.upi_id = request.form.get('upi_id')
        profile.payee_name = request.form.get('payee_name') 
        profile.terms = request.form.get('terms')
        
        profile.youtube_channel_url = request.form.get('youtube_channel_url')
        profile.intro_video_url = request.form.get('intro_video_url')
        
        db.session.commit()
        flash('Business settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', business=profile)