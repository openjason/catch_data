import imaplib


connection = imaplib.IMAP4_SSL(HOSTNAME)
connection.login(USERNAME, PASSWORD)

new_message = email.message.Message()
new_message["From"] = "hello@itsme.com"
new_message["Subject"] = "My new mail."
new_message.set_payload("This is my message.")

connection.append('INBOX', '', imaplib.Time2Internaldate(time.time()), str(new_message))