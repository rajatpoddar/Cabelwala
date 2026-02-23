from flask import Flask
from config import Config
from models import db, Admin
from routes.public import public_bp
from routes.admin import admin_bp
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'admin.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create initial database and default admin
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            default_admin = Admin(
                username='admin', 
                password_hash=generate_password_hash('password123')
            )
            db.session.add(default_admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)