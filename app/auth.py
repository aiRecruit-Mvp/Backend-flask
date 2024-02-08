from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from app import mail
import random
import string
def hash_password(password):
    return generate_password_hash(password)

def verify_password(hash, password):
    return check_password_hash(hash, password)


# Function to generate a random verification code
def generate_random_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_email(recipient, subject, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)
# Function to send an email with the verification code
def send_verification_email(email, verification_code):
    subject = "Password Reset Verification Code"
    body = f"Your verification code is: {verification_code}"
    msg = Message(subject, recipients=[email], body=body)
    try:
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

