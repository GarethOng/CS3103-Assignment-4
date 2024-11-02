#!/usr/bin/env python3

import argparse
import sys
import csv
import os
import re
from typing import Optional, List, Dict, Tuple, Set
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    # Replace with your actual email and password
    from_email = "limyanling2002@gmail.com" # Please test with ur own gmail
    password = "bisb keyn uhwj jqwo" #Please test with your own password

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



def is_valid_email(email: str) -> bool:
    """
    Basic email validation using regex.
    credit: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def get_available_departments(filepath: str) -> Set[str]:
    """
    Extract all unique department codes from the CSV file.
    """
    departments = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            departments = {row['department_code'].strip() for row in reader if row.get('department_code')}
    except Exception:
        pass
    return departments

def validate_department_code(department: str, filepath: str) -> Tuple[bool, Optional[str]]:
    """
    Validate the department code against available departments in the CSV.
    Returns (is_valid, error_message).
    """
    if department.lower() == 'all':
        return True, None
        
    available_departments = get_available_departments(filepath)
    if not available_departments:
        return False, "Could not read departments from CSV file"
        
    if department not in available_departments:
        departments_list = ', '.join(sorted(available_departments))
        return False, f"Invalid department code. Available departments are: {departments_list}"
        
    return True, None

def validate_csv_file(filepath: str) -> Tuple[bool, List[str]]:
    """
    Validate that the CSV file exists and has the required format.
    Returns a tuple of (is_valid, list_of_errors).
    """
    errors = []
    
    if not os.path.exists(filepath):
        return False, ["CSV file does not exist"]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            header = next(reader, None)
            if not header:
                return False, ["CSV file is empty"]
            
            header = [col.lower().strip() for col in header]
            required_columns = {'email', 'name', 'department_code'}
            missing_columns = required_columns - set(header)
            
            if missing_columns:
                return False, [f"Missing required columns: {', '.join(missing_columns)}"]
            
            email_idx = header.index('email')
            name_idx = header.index('name')
            dept_idx = header.index('department_code')
            
            row_number = 2
            for row in reader:
                if not row:
                    continue
                
                if len(row) != len(header):
                    errors.append(f"Row {row_number}: Invalid number of columns")
                    continue
                
                email = row[email_idx].strip()
                if not email:
                    errors.append(f"Row {row_number}: Empty email address")
                elif not is_valid_email(email):
                    errors.append(f"Row {row_number}: Invalid email format - {email}")
                
                name = row[name_idx].strip()
                if not name:
                    errors.append(f"Row {row_number}: Empty name")
                elif len(name) < 2:
                    errors.append(f"Row {row_number}: Name too short - {name}")
                
                dept_code = row[dept_idx].strip()
                if not dept_code:
                    errors.append(f"Row {row_number}: Empty department code")
                
                row_number += 1
            
            if row_number == 2:
                errors.append("CSV file contains no data rows")
            
            return len(errors) == 0, errors
            
    except csv.Error as e:
        return False, [f"CSV parsing error: {str(e)}"]
    except Exception as e:
        return False, [f"Unexpected error while reading CSV: {str(e)}"]

def read_file_contents(filepath: str) -> Optional[str]:
    """
    Read and return the contents of a file.
    Returns None if file doesn't exist or can't be read.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return None

def validate_html_file(filepath: str) -> bool:
    """
    Validate that the HTML body file exists and contains some content.
    """
    content = read_file_contents(filepath)
    return bool(content and content.strip())

def get_recipients_by_department(filepath: str, department: str) -> List[Dict[str, str]]:
    """
    Get list of recipients filtered by department code.
    If department is 'all', returns all recipients.
    """
    recipients = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (department.lower() == 'all' or 
                    row['department_code'].strip() == department):
                    recipients.append({
                        'email': row['email'].strip(),
                        'name': row['name'].strip(),
                        'department_code': row['department_code'].strip()
                    })
    except Exception as e:
        print(f"Error reading recipients: {str(e)}")
        return []
    
    return recipients

def main():
    parser = argparse.ArgumentParser(
        description='Send emails to recipients specified in a CSV file with a custom subject and HTML body.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  mailer -r recipients.csv -s "CS3103 Assignment 5 Release" -b email_body.html -d CS3103 
  mailer -r recipients.csv -s "Cancellation of Finals for AY2024/25 SEM 1" -b email_body.html -d all

CSV file format:
  The CSV file must contain the following columns:
    - email: Valid email address
    - name: Recipient's name
    - department_code: Department identifier

  Example:
    email,name,department_code
    gareth@u.nus.edu ,Gareth, ABC123     
    nevin@u.nus.edu ,Nevin , DEF456      
    alvin@u.nus.edu ,Alvin , GHI789      
    yan.ling@u.nus.edu ,Yan Ling, JKL101

HTML body file:
  The body file should contain valid HTML content with optional placeholders:
  Example:
    <html><body><h1>Hello {name}!</h1><p>Department: {department_code}</p></body></html>
        """
    )

    parser.add_argument(
        '-r', '--recipients',
        required=True,
        help='Path to the CSV file containing recipient information'
    )
    
    parser.add_argument(
        '-s', '--subject',
        required=True,
        help='Subject line for the email'
    )
    
    parser.add_argument(
        '-b', '--body',
        required=True,
        help='Path to the HTML file containing the email body'
    )
    
    parser.add_argument(
        '-d', '--department',
        required=True,
        help='Department code to filter recipients (use "all" for all departments)'
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return

    validation_errors = []

    # Validate CSV file
    csv_is_valid, csv_errors = validate_csv_file(args.recipients)
    if not csv_is_valid:
        validation_errors.extend(csv_errors)
    
    # Validate department code
    dept_is_valid, dept_error = validate_department_code(args.department, args.recipients)
    if not dept_is_valid:
        validation_errors.append(f"Error: {dept_error}")

    # Validate subject
    if not args.subject.strip():
        validation_errors.append("Error: Subject cannot be empty.")

    # Validate HTML body file
    if not os.path.exists(args.body):
        validation_errors.append(f"Error: Body file '{args.body}' does not exist.")
    elif not validate_html_file(args.body):
        validation_errors.append(f"Error: '{args.body}' is not a valid HTML file or is empty.")

    if validation_errors:
        print("\nValidation Errors:")
        for error in validation_errors:
            print(f"- {error}")
        print("\nUse -h or --help for usage information.")
        sys.exit(1)

    # Get filtered recipients
    recipients = get_recipients_by_department(args.recipients, args.department)
    
    if not recipients:
        print(f"\nNo recipients found for department: {args.department}")
        sys.exit(1)

    # Read HTML template
    html_content = read_file_contents(args.body)
    # SMTP server configuration
   

    # Send emails to each recipient
    success_count = 0
    failure_count = 0
    for recipient in recipients:
    # Replace placeholders in the email body with recipient's details
        personalized_body = f"""
            Hello {recipient['name']}!
            Welcome to the {recipient['department_code']} department.

            This is a test email template.
            """

        # Send the email and check if it was successful
        try:
            send_email(
                to_email=recipient['email'],
                subject=args.subject,
                body=personalized_body
            )
            print(f"Email successfully sent to {recipient['name']} ({recipient['email']})")
            success_count += 1
        except Exception as e:
            print(f"Failed to send email to {recipient['name']} ({recipient['email']}): {e}")
            failure_count += 1

    print(f"\nEmail sending completed. {success_count} emails sent successfully, {failure_count} failures.")

    
    print(f"""
Valid arguments received:
- Recipients file: {args.recipients}
- Subject: {args.subject}
- Body file: {args.body}
- Department: {args.department}

Recipients to process: {len(recipients)}
Department filter: {"All departments" if args.department.lower() == 'all' else args.department}

recipients:
{'-' * 40}""")
    
    for recipient in recipients:
        print(f"- {recipient['name']} ({recipient['email']}) - {recipient['department_code']}")

    print(f"\nNext steps would be to:")
    print("1. Process the HTML template for each recipient")
    print("2. Send emails to all recipients in the filtered list")
    print("3. Generate success/failure report")

if __name__ == "__main__":
    main()
