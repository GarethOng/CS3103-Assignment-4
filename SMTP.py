import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

def send_email(to_email, subject, body):
    # Replace with your actual email and password
    from_email = "" # Please test with ur own gmail
    password = "" #Please test with your own password

    # Set up the SMTP server with SSL (e.g., for Gmail)
    smtp_server = "smtp.gmail.com"
    port = 465

    try:
        # Establish an SSL connection
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            # Login to the email account
            server.login(from_email, password)
            
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Send the email
            server.sendmail(from_email, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
    
    except smtplib.SMTPException as e:
        print(f"Error: {e}")

# Test the function with delay
subject = "Test Email"
body = "<html><body><h1>Hello, #name#</h1><p>This is a test email for #department# department.</p></body></html>"

# you can parse the csv file here
email_list = [
    ("e0774088@u.nus.edu", "Alice", "HR"),
    ("limyanling2002@gmail.com", "BOB", "IT")
    
]

for email, name, department in email_list:
    personalized_body = body.replace("#name#", name).replace("#department#", department)
    send_email(email, subject, personalized_body)
    time.sleep(5)  # Introduce delay between emails
