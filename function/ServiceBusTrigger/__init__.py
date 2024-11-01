import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from azure.functions import ServiceBusMessage
import psycopg2
import os
import smtplib

def main(msg: ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('ServiceBus queue trigger processed message: %s', notification_id)
    
    connection = None
    cursor = None
    
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            host=os.getenv("DATABASE_HOSTNAME")
        )
        cursor = connection.cursor()

        # Get notification message and subject from database using the notification_id
        cursor.execute(
            '''SELECT subject, message
               FROM notification
               WHERE id = %s''', (notification_id,)
        )
        notification = cursor.fetchone()

        if not notification:
            logging.warning('No notification found with id %s', notification_id)
            return

        # Get attendees email and name
        cursor.execute('''SELECT first_name, last_name, email FROM attendee''')
        attendees = cursor.fetchall()

        # Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            first_name, last_name, email = attendee
            subject = '{} {}: {}'.format(first_name, last_name, notification[0])
            send_email(email, subject, notification[1])

       # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        notification_status = 'Notified {} attendees'.format(len(attendees))
        cursor.execute(
            '''UPDATE notification
               SET status = %s, completed_date = %s
               WHERE id = %s''', (notification_status, datetime.datetime.utcnow(), notification_id)
        )
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error('Error: %s', error)
        if connection:
            connection.rollback()

    finally:
        # Close connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def send_email(email, subject, body):
    smtp_server = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    message = MIMEMultipart()
    message['From'] = smtp_email
    message['To'] = email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_email, smtp_password)  # Log in to your account
        server.sendmail(smtp_email, email, message.as_string())  # Send the email
        server.quit()  # Disconnect from the server
        
        logging.info("Function - send_email: send_email successfully.")
    except Exception as e:
        logging.error(f"Function - send_email:>>> send_email failed: {e}")
