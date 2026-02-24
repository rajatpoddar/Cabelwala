from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from models import db, Project, BusinessProfile, ServiceRequest

public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_request = ServiceRequest(
            name=request.form.get('req_name'),
            mobile=request.form.get('req_mobile'),
            service=request.form.get('req_service'),
            address=request.form.get('req_address')
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Your request has been submitted successfully! Our team will contact you soon.', 'success')
        return redirect(url_for('public.index') + '#request-service')

    business = BusinessProfile.query.first()
    fiber_projects = Project.query.filter_by(category='Fiber').order_by(Project.created_at.desc()).limit(6).all()
    cctv_projects = Project.query.filter_by(category='CCTV').order_by(Project.created_at.desc()).limit(6).all()
    return render_template('public/index.html', business=business, fiber_projects=fiber_projects, cctv_projects=cctv_projects)

# Naya Route: Public PDF Link ke liye
@public_bp.route('/bill/view/<filename>')
def view_bill(filename):
    try:
        return send_from_directory(current_app.config['INVOICE_FOLDER'], filename)
    except Exception as e:
        return "Bill not found!", 404