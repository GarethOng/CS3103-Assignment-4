#!/usr/bin/env python3

import argparse
import sys
import csv
import os
import re
from typing import Optional, List, Dict, Tuple, Set
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

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

import smtplib
from email.message import EmailMessage

def send_email(email:str, password:str, recipient: dict, subject: str, body: str) -> bool:
    """
    Send an email to the specified recipient.
    """
    
    try:
        # Connect to Gmail's SMTP server (replace with your SMTP server if different)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            # Login to the email account
            server.login(email, password)
            
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = recipient['email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server.sendmail(email, recipient['email'], msg.as_string())
            return True
    except Exception as e:
        print(f"Failed to send to {recipient['email']}: {e}")
        return False

# Sends a GET request to the server to get the number of people who opened the mail
def viewCount():
    url='https://d8afcuwcu1.execute-api.us-east-2.amazonaws.com/default/viewCount'
    response=requests.get(url)
    print(f'Number of recipients who opened the mail: {response.json()}')
    
def main():
    parser = argparse.ArgumentParser(
        description='Email sending and tracking tool.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Create mutually exclusive group for commands
    command_group = parser.add_mutually_exclusive_group(required=True)
    
    # Add viewcount command
    command_group.add_argument(
        '-viewcount',
        action='store_true',
        help='Retrieve view count statistics'
    )

    # Add send email command
    command_group.add_argument(
        '-send',
        action='store_true',
        help='Send emails to recipients'
    )

    # Add all other arguments as optional, they'll be required only when sending emails
    parser.add_argument(
        '-r', '--recipients',
        help='Path to the CSV file containing recipient information'
    )
    
    parser.add_argument(
        '-s', '--subject',
        help='Subject line for the email'
    )
    
    parser.add_argument(
        '-b', '--body',
        help='Path to the HTML file containing the email body'
    )
    
    parser.add_argument(
        '-d', '--department',
        help='Department code to filter recipients (use "all" for all departments)'
    )

    parser.add_argument(
        '-e', '--email',
        help='source email that the emails will be sent out from'
    )

    parser.add_argument(
        '-p', '--password',
        help='password for the source email'
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return

    # Handle viewcount command
    if args.viewcount:
        print("Retrieving view count statistics...")
        viewCount()
        return

    # Handle send email command
    if args.send:
        # Validate required arguments for sending emails
        required_args = {
            'recipients': args.recipients,
            'subject': args.subject,
            'body': args.body,
            'department': args.department,
            'email': args.email,
            'password': args.password
        }

        missing_args = [arg for arg, value in required_args.items() if not value]
        
        if missing_args:
            print("\nError: The following arguments are required for sending emails:")
            for arg in missing_args:
                print(f"  -{arg[0]}/--{arg}")
            print("\nUse -h or --help for usage information.")
            sys.exit(1)

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

        email_count_by_department = defaultdict(int)

        for recipient in recipients:
            # Personalize HTML content for the recipient
            personalized_content = html_content.format(
                name=recipient['name'], 
                department_code=recipient['department_code']
            )
            
            if send_email(args.email, args.password, recipient, args.subject, personalized_content):
                email_count_by_department[recipient['department_code']] += 1

        print("\nEmail Send Report:")
        print("-" * 40)
        if args.department.lower() == "all":
            # If "all" is specified, show counts for each department
            for dept_code, count in email_count_by_department.items():
                print(f"Department: {dept_code}, Emails Sent: {count}")
        else:
            # If a specific department is specified, show only that department's count
            total_emails = sum(email_count_by_department.values())
            print(f"Department: {args.department}, Emails Sent: {total_emails}")

        print("\nReport generation completed.")

#     print(f"""
# Valid arguments received:
# - Recipients file: {args.recipients}
# - Subject: {args.subject}
# - Body file: {args.body}
# - Department: {args.department}

# Recipients to process: {len(recipients)}
# Department filter: {"All departments" if args.department.lower() == 'all' else args.department}

# recipients:
# {'-' * 40}""")
    
#     for recipient in recipients:
#         print(f"- {recipient['name']} ({recipient['email']}) - {recipient['department_code']}")

#     print(f"\nNext steps would be to:")
#     print("1. Process the HTML template for each recipient")
#     print("2. Send emails to all recipients in the filtered list")
#     print("3. Generate success/failure report")

if __name__ == "__main__":
    main()
