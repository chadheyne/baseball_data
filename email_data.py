#!/usr/bin/env python3
import os, re
import smtplib

from email import encoders

from email.mime.base import MIMEBase

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def zipdir(path, zipfile):
    for root, dirs, files in os.walk(path):
        for f in files:
            if not f.endswith('.csv'):
                continue
            zipfile.write(os.path.join(root, f) )


def send_email(date, directory, sendZip = True):
 
    sender = 'heyne.chad@gmail.com'
    password = "cmh070989"
    recipient = 'chadheyne@gmail.com'
    message = 'Data attached for {0}.'.format(date)
 

 

    msg = MIMEMultipart()
    msg['Subject'] = 'Results for today ({0})'.format(date)
    msg['To'] = recipient
    msg['From'] = sender

    msg.attach( MIMEText(message) )

    
    if sendZip:
        import zipfile
        import tempfile

        zf = tempfile.TemporaryFile(prefix='mail', suffix = '.zip')
        ziparchive = zipfile.ZipFile(zf, 'w')
        zipdir(directory, ziparchive)
        ziparchive.close()
        zf.seek(0)



        part = MIMEBase('application', 'zip')
        part.set_payload( zf.read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename= "Data" + date + ".zip")
        msg.attach(part)

    else:
        files = os.listdir(directory)
        csvsearch = re.compile(".csv", re.IGNORECASE)
        files = list(filter(csvsearch.search, files))
        for filename in files:

            path =  os.path.abspath(os.path.join(directory, filename))
            if not os.path.isfile(path):
                continue

            part = MIMEBase('application', 'octet-stream')
            part.set_payload( open(path, "rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(part)

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)

    session.sendmail(sender, recipient, msg.as_string())
    session.quit()
    return True
