import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(dir_path,files,toaddr):

    msg = MIMEMultipart()
#    msg['To'] = "openjc@163.com"
    msg['To'] = ";".join(toaddr)
    msg['From'] = "openjc@163.com"
    msg['Subject'] = "test for python send email"

    html = """\
    xxx,
        你好，这是一个测试邮件，
        附件："""
    html = html + str(files[0])+','+ str(files[1])
    html = html +"""
    请不要拦截我的邮件。MIMEText(content,_subtype='html',_charset='gb2312') 
    """
    body = MIMEText(html, 'plain')
#    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read())
        attachment.add_header('Content-Disposition','attachment', filename=f)
        msg.attach(attachment)

#    toaddr = ('openjc@163.com','zhjcc@163.com','chenjiancheng@eastcompeace.com')
#    toaddr = 'chenjiancheng@eastcompeace.com'
    fromaddr = 'openjc@163.com'
    server = smtplib.SMTP('smtp.163.com', 25)
#    server = smtplib.SMTP('mail.eastcompeace.com', 25)
    server.starttls()
    server.login(fromaddr, "cnet")
    mailbody = msg.as_string()

    server.sendmail(fromaddr, toaddr, mailbody)
    server.quit()

    # try:
    #     server.sendmail(fromaddr, toaddr, mailbody)
    # except (TypeError, ValueError) as e:  # 捕捉多个异常，并将异常对象输出
    #     print(e)
    # except:  # 捕捉其余类型异常
    #     print("it's still wrong")
    # finally:
    #     server.quit()

if __name__ == '__main__':
    dir_path = "e:\\test\\"
    file_list = ["cfg_new.xlsx", "killwpssch.bat","log.txt"]
    toaddr = ('openjc@139.com', 'zhjcc@163.com', 'chenjiancheng@eastcompeace.com')
    send_email(dir_path,file_list,toaddr)










