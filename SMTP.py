import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import requests

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
body = "<html><body><h1>Hello, #name#</h1><p>This is a test email for #department# department.</p><img src='https://2knd1q800d.execute-api.us-east-2.amazonaws.com/default/getImage' width='1px' height='1px'></body></html>"


import pandas as pd

# parse the csv file here
def parse_mail_data(file_path, department_code="all"):
    df = pd.read_excel(file_path)
    
    if department_code != "all":
        df = df[df['DepartmentCode'] == department_code] #filters csv based on department code if specified, or select all rows if 'all'
    
    records = list(df.itertuples(index=False, name=None))
    return records

file_path = "" # replace this with the file path to csv file containing the email, names and dept codes.
#eg. "/workspaces/CS3103-Assignment-4/sample.xlsx"
department_code = "" #replace this with the desired department code and if the department code is “all” then the mails should be send to all email ids in the list.


email_list = parse_mail_data(file_path, department_code)
# email_list = [
#     ("e0774088@u.nus.edu", "Alice", "HR"),
#     ("limyanling2002@gmail.com", "BOB", "IT")
# ]

print(email_list)
for email, name, department in email_list:
    personalized_body = body.replace("#name#", name).replace("#department#", department)
    send_email(email, subject, personalized_body)
    time.sleep(5)  # Introduce delay between emails

# Sends a GET request to the server to get the number of people who opened the mail
def viewCount():
    url='https://d8afcuwcu1.execute-api.us-east-2.amazonaws.com/default/viewCount'
    response=requests.get(url)
    print(f'Number of recipients who opened the mail: {response.json()}')