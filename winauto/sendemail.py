import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_selenium_report(dir_path,files):

    msg = MIMEMultipart()
    msg['To'] = "openjc@163.com"
    msg['From'] = "chenjiancheng@eastcompeace.com"
    msg['Subject'] = "test for python send email"
    text_body = 'You will not see this in a MIME-aware mail reader.\n ' \
                'HHHHH \n OK'

    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read())
        attachment.add_header('Content-Disposition','attachment', filename=f)
        msg.attach(attachment)

    toaddr = 'openjc@163.com'
    fromaddr = 'chenjiancheng@eastcompeace.com'
#    server = smtplib.SMTP('smtp.163.com', 25)
    server = smtplib.SMTP('mail.eastcompeace.com', 25)
    server.starttls()
    server.login(fromaddr, "password")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == '__main__':
    dir_path = "e:\\test\\"
    files = ["cfg_new.xlsx", "clearexpdir.py", "killwpssch.bat"]
    send_selenium_report(dir_path,files)






















# test

# import smtplib
# import base64
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
#
# fromaddr = "openjc@163.com"
# toaddr = 'openjc@163.com'
#
# msg = MIMEMultipart()
#
# msg['From'] = fromaddr
# msg['To'] = toaddr
# msg['Subject'] = "SUBJECT OF THE EMAIL"
#
# body = "TEXT YOU WANT TO SEND"
#
# msg.attach(MIMEText(body, 'plain'))
#
# filename = "sw3.log.xlsx"
# attachment = open("e:\\test\\cfg_new.xlsx", "rb")
#
# part = MIMEBase('application', 'octet-stream')
# part.set_payload((attachment).read())
# encoders.encode_base64(part)
# part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
#
# msg.attach(part)
#
# server = smtplib.SMTP('smtp.163.com', 25)
# server.starttls()
# server.login(fromaddr, "1637jccnet")
# text = msg.as_string()
# server.sendmail(fromaddr, toaddr, text)
# server.quit()
