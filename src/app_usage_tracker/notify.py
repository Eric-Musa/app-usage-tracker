from email.message import EmailMessage
import logging
import os
import platform
import smtplib

from .scheduling import (
    DATE_FORMAT,
)


def scrape_message(scrape_data):
    return "\n".join(["%s [%s]: %s" % _ for _ in scrape_data])


def send_summary_email(
    data,
    daystamp,
    to_email,
    from_email,
    from_email_pwd=os.environ["APP_USAGE_TRACKER_EMAIL_PWD"],
):
    msg = EmailMessage()
    msg[
        "Subject"
    ] = f"App Usage on {platform.node()} for \
        {daystamp.strftime(DATE_FORMAT)}"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(scrape_message(data))

    s = smtplib.SMTP("smtp.gmail.com:587")
    s.ehlo()
    s.starttls()
    s.login(from_email, from_email_pwd)

    response = s.send_message(msg)
    if response:
        logging.warn(
            "SMTP email response returned the following: " + str(response)
        )
    s.quit()
    return response
