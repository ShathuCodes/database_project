# pyrefly: ignore [missing-import]
from flask import Flask, render_template    
# pyrefly: ignore [missing-import]
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    
    from app.config import Config
    app.config.from_object(Config)

    # ── Flask-Login setup ──────────────────────────────────────
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.models import load_user
    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)

    # ── Register Blueprints ────────────────────────────────────
    from app.routes.auth       import auth_bp
    from app.routes.dashboard  import dashboard_bp
    from app.routes.patients   import patients_bp
    from app.routes.cases      import cases_bp
    from app.routes.postmortem import postmortem_bp
    from app.routes.clinical   import clinical_bp
    from app.routes.skeletal   import skeletal_bp
    from app.routes.evidence   import evidence_bp
    from app.routes.lab        import lab_bp
    from app.routes.reports    import reports_bp
    from app.routes.staff      import staff_bp
    from app.routes.users      import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp,   url_prefix='/patients')
    app.register_blueprint(cases_bp,      url_prefix='/cases')
    app.register_blueprint(postmortem_bp, url_prefix='/postmortem')
    app.register_blueprint(clinical_bp,   url_prefix='/clinical')
    app.register_blueprint(skeletal_bp,   url_prefix='/skeletal')
    app.register_blueprint(evidence_bp,   url_prefix='/evidence')
    app.register_blueprint(lab_bp,        url_prefix='/lab')
    app.register_blueprint(reports_bp,    url_prefix='/reports')
    app.register_blueprint(staff_bp,      url_prefix='/staff')
    app.register_blueprint(users_bp,      url_prefix='/users')

    # ── Error pages ────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html',
            code=403, message='Forbidden',
            detail='You do not have permission to access this page.'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
            code=404, message='Page Not Found',
            detail='The page you requested could not be found.'), 404

    return app
