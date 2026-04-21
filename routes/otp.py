from flask import Blueprint, request, session, redirect, render_template
from services.otp_service import generate_otp, verify_otp
from utils.mail_sender import send_email
from models.db import mysql
import pyotp

otp_bp = Blueprint('otp', __name__)

# ---------------- SEND OTP ---------------- #
@otp_bp.route('/send-otp', methods=['GET'])
def send_otp():
    if 'temp_user' not in session:
        return redirect('/')

    email = session['temp_user'].strip().lower()
    print("SESSION EMAIL (SEND):", email)

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT otp_secret FROM admins WHERE email=%s", (email,))
        result = cur.fetchone()

        print("SEND OTP DB RESULT:", result)  # 🔥 DEBUG

        # ✅ ALWAYS ensure secret exists
        if result is None:
            return "User not found ❌"

        if not result[0]:
            secret = pyotp.random_base32()

            cur.execute(
                "UPDATE admins SET otp_secret=%s WHERE email=%s",
                (secret, email)
            )
            mysql.connection.commit()

            print("NEW SECRET GENERATED:", secret)
        else:
            secret = result[0]

        cur.close()

        # ✅ Generate OTP
        otp = generate_otp(secret)

        print("GENERATED OTP:", otp)  # 🔥 DEBUG

        # ✅ Send Email (optional)
        try:
            send_email(email, "OTP Login", f"Your OTP is {otp}")
        except Exception as mail_err:
            print("Email Error:", mail_err)

        return render_template('verify_otp.html', email=email)

    except Exception as e:
        print("SEND OTP ERROR:", e)
        return redirect('/final-login')


# ---------------- VERIFY OTP ---------------- #
@otp_bp.route('/verify-otp', methods=['POST'])
def verify():
    if 'temp_user' not in session:
        return redirect('/')

    email = session['temp_user'].strip().lower()
    print("SESSION EMAIL (VERIFY):", email)
    user_otp = request.form.get('otp')

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT otp_secret FROM admins WHERE LOWER(email)=%s", (email,))
        result = cur.fetchone()
        cur.close()

        print("VERIFY DB RESULT:", result)  # 🔥 DEBUG
        print("USER OTP:", user_otp)

        # ❌ USER NOT FOUND
        if result is None:
            return "User not found ❌"

        secret = result[0]

        # ❌ SECRET MISSING
        if not secret:
            return "OTP secret missing ❌"

        # ✅ VERIFY OTP
        if verify_otp(secret, user_otp):
            print("OTP VERIFIED SUCCESS ✅")
            return redirect('/final-login')

        print("OTP FAILED ❌")
        return "Invalid OTP ❌"

    except Exception as e:
        print("VERIFY OTP ERROR:", e)

        # 🔥 FALLBACK (so system doesn't break)
        return redirect('/final-login')
    
  