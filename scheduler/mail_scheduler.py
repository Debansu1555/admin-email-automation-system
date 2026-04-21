from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from routes.email import send_mail
from models.db import mysql

def check_mails(app):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM emails WHERE status='pending'")
        mails = cur.fetchall()

        for mail in mails:
            if datetime.now() >= mail[5]:
                send_mail(mail[2], mail[3], mail[4], mail[7])
                cur.execute("UPDATE emails SET status='sent' WHERE id=%s", (mail[0],))
                mysql.connection.commit()

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: check_mails(app), trigger="interval", seconds=30)
    scheduler.start()