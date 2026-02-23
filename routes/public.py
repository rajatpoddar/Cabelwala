from flask import Blueprint, render_template
from models import Project

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    fiber_projects = Project.query.filter_by(category='Fiber').order_by(Project.created_at.desc()).limit(6).all()
    cctv_projects = Project.query.filter_by(category='CCTV').order_by(Project.created_at.desc()).limit(6).all()
    return render_template('public/index.html', fiber_projects=fiber_projects, cctv_projects=cctv_projects)