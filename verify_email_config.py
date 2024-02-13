from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

@app.route('/send_test_email', methods=['GET'])
def send_test_email():
    # Email server settings
    smtp_server = 'your_smtp_server_address'
    smtp_port = 587  # or 25 for non-SSL connections
    smtp_username = 'your_smtp_username'
    smtp_password = 'your_smtp_password'

    sender_email = 'your_sender_email@example.com'
    recipient_email = 'recipient_email@example.com'

    # Create a MIME message
    message = MIMEMultipart()
    message['achref.chaabani@esprit.tn'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Test Email'
    body = 'This is a test email from Python.'
    message.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

        # Close the connection
        server.quit()

        return 'Test email sent successfully.'
    except Exception as e:
        return f'Error sending test email: {e}'

if __name__ == '__main__':
    app.run(debug=True)
