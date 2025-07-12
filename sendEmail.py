import os
import smtplib

class SendEmail:
    def __init__(self):
        self.connection = smtplib.SMTP('smtp.gmail.com', 587)
        self.connection.starttls()
        self.connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("PASS"))

    def send_email(self, user_email, message, user_phone, user_name):
        self.connection.sendmail(from_addr=os.environ.get("MY_EMAIL"), to_addrs=os.environ.get("MY_EMAIL"), msg=f"Subject: Email form {user_name}\n\n{user_email}\n{user_phone}\n{message}")
        self.connection.sendmail(from_addr=os.environ.get("MY_EMAIL"), to_addrs=user_email, msg=f"Subject: My First Blog\n\nEmail has been sent\nI will answer as soon as possible.\nHave a nice day Alex.")
        self.connection.quit()
