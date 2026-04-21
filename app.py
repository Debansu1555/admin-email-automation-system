import os
from flask import Flask, render_template
from models.db import mysql
import config

from routes.auth import auth_bp
from routes.otp import otp_bp
from routes.face_auth import face_bp
from routes.biometric import biometric_bp
from routes.admin import admin_bp
from routes.email import email_bp
from routes.webauthn import webauthn_bp

from scheduler.mail_scheduler import start_scheduler


def create_app():            # Factory function to create Flask app
    app = Flask(__name__)

    app.config.from_object(config)       
    app.secret_key = 'secret123'

    app.config.update(                   
        SESSION_COOKIE_SAMESITE="Lax",   
        SESSION_COOKIE_SECURE=False,
    )

    mysql.init_app(app)   # Initialize MySQL with app context

    # ✅ Register APIs
    app.register_blueprint(auth_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(face_bp)
    #app.register_blueprint(biometric_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(webauthn_bp, url_prefix='/webauthn')

    # ===============================
    # ✅ ADD THESE PAGE ROUTES
    # ===============================
    @app.route('/register-fingerprint')              #✅ new route for fingerprint registration page
    def register_fingerprint_page():
        print("REGISTER PAGE LOADED")
        return render_template('register_fingerprint.html')

    @app.route('/fingerprint-login')                 #✅ new route for fingerprint login page
    def fingerprint_login_page():
        return render_template('fingerprint_login.html')

    with app.app_context():                          #✅ start scheduler within app context
        start_scheduler(app)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
