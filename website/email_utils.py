'''This module contains utility functions for sending emails.'''
from flask_mail import Message
from flask import current_app

def send_email(subject, recipient, body):
    '''Function to send an email'''
    # Access mail from current_app context to avoid direct import
    mail = current_app.extensions['mail']

    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    with current_app.app_context():
        mail.send(msg)
