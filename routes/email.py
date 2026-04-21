from flask import Blueprint, render_template, request
from models.db import mysql
import smtplib
from email.mime.text import MIMEText
import config

email_bp = Blueprint('email', __name__)


# 🔹 Get all sender emails from DB
def get_senders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM sender_emails")
    return cur.fetchall()


# 🔹 Send email function (UPDATED)
def send_mail(to, subject, message, sender_email):
    msg = MIMEText(message, 'html')   # HTML support
    msg['Subject'] = subject
    msg['From'] = sender_email        # 👈 dynamic sender
    msg['To'] = to

    server = smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT)
    server.starttls()
    server.login(config.EMAIL_USER, config.EMAIL_PASS)
    server.send_message(msg)
    server.quit()


# 🔹 Route
@email_bp.route('/send_email', methods=['GET', 'POST'])
def send_email():
    senders = get_senders()   # 👈 fetch sender list

    if request.method == 'POST':
        sender = request.form['sender']   # 👈 selected sender
        to = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        time = request.form['time']

        if time:
            cur = mysql.connection.cursor()
            cur.execute("""
            INSERT INTO emails (sender,receiver,subject,message,scheduled_time,status,display_sender)
            VALUES (%s,%s,%s,%s,%s,'pending',%s)
            """, ('system', to, subject, message, time, sender))
            mysql.connection.commit()
        else:
            send_mail(to, subject, message, sender)

        return "Email Sent Successfully"

    return render_template('send_email.html', senders=senders)