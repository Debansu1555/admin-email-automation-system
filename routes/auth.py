from flask import Blueprint, request, session, redirect, render_template, url_for
from flask_mysqldb import MySQL

mysql = MySQL()

auth_bp = Blueprint('auth', __name__)

# ---------------- LOGIN ---------------- #
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        # supports both new HTML name="login_type" and old name="method"
        login_type = request.form.get('login_type', '').strip().lower()
        if not login_type:
            login_type = request.form.get('method', '').strip().lower()

        print("LOGIN EMAIL:", email)
        print("LOGIN PASSWORD:", password)
        print("LOGIN TYPE:", login_type)

        if not email or not password or not login_type:
            return "All fields are required ❌", 400

        cur = mysql.connection.cursor()

        # Debug: check whether email exists first
        cur.execute("SELECT * FROM admins WHERE LOWER(email) = %s", (email,))
        email_row = cur.fetchone()
        print("EMAIL ROW:", email_row)

        # Main login check
        cur.execute(
            "SELECT * FROM admins WHERE LOWER(email) = %s AND password = %s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        print("MATCHED USER:", user)

        if user:
            session['temp_user'] = email

            # safer role extraction
            # change index if your role column is not at position 4
            session['temp_role'] = user[4]

            print("SESSION SET:", session.get('temp_user'))
            print("ROLE SET:", session.get('temp_role'))

            if login_type == 'otp':
                return redirect(url_for('otp.send_otp'))

            elif login_type == 'face':
                return redirect(url_for('face.face_login'))

            elif login_type == 'fingerprint':
                return redirect(url_for('fingerprint_login_page'))

            else:
                return f"Invalid authentication type: {login_type} ❌", 400

        return "Invalid login credentials ❌", 401

    return render_template('login.html')


# ---------------- FINAL LOGIN ---------------- #
@auth_bp.route('/final-login', methods=['GET'])
def final_login():
    print("FINAL LOGIN HIT")

    if 'temp_user' in session:
        session['user'] = session['temp_user']
        session['role'] = session['temp_role']

        session.pop('temp_user', None)
        session.pop('temp_role', None)

        print("FINAL SESSION USER:", session.get('user'))
        print("FINAL SESSION ROLE:", session.get('role'))

        if session['role'] == 'super':
            return redirect(url_for('admin.super_dashboard'))
        else:
            return redirect(url_for('admin.sub_dashboard'))

    return redirect(url_for('auth.login'))


# ---------------- LOGOUT ---------------- #
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))