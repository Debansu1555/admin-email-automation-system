from flask import Blueprint, render_template, request, redirect, flash
from models.db import mysql

admin_bp = Blueprint('admin', __name__)


# ✅ Super Admin Dashboard
@admin_bp.route('/super_dashboard', methods=['GET'])
def super_dashboard():
    return render_template('dashboard_super.html')


# ✅ Sub Admin Dashboard
@admin_bp.route('/sub_dashboard', methods=['GET'])
def sub_dashboard():
    return render_template('dashboard_sub.html')


# ✅ Create Sub Admin (UPDATED)
@admin_bp.route('/create_subadmin', methods=['GET', 'POST'])
def create_subadmin():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        position = request.form.get('position')
        phone = request.form.get('phone')

        # 🔴 Basic Validation
        if not name or not email or not password:
            flash("All required fields must be filled!", "error")
            return redirect('/create_subadmin')

        try:
            cur = mysql.connection.cursor()

            # 🔍 Check if email already exists
            cur.execute("SELECT * FROM admins WHERE email=%s", (email,))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Email already exists!", "error")
                return redirect('/create_subadmin')

            # ✅ Insert new sub admin
            cur.execute("""
            INSERT INTO admins (name,email,password,role,position,phone)
            VALUES (%s,%s,%s,'sub',%s,%s)
            """, (name, email, password, position, phone))

            mysql.connection.commit()

            flash("Sub Admin created successfully!", "success")
            return redirect('/super_dashboard')

        except Exception as e:
            print("Error:", e)
            flash("Something went wrong!", "error")
            return redirect('/create_subadmin')

    return render_template('create_subadmin.html')