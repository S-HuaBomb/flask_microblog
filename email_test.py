import smtplib
from email.mime.text import MIMEText
from email.header import Header


class Mail:
    def __init__(self):
        self.mail_host = 'smtp.qq.com'  # QQ邮箱服务器
        self.mail_password = 'waktqkcdjkyhfbbg'  # QQ邮箱授权码
        self.sender = '1712317024@qq.com'
        self.receivers = ['s_huabang@163.com', '1712317024@qq.com']

    def send(self):
        content = 'Hi, from python'
        msg = MIMEText(content, 'plain', 'utf-8')  # 邮件内容

        msg['From'] = Header('python', 'utf-8')
        msg['To'] = Header('mail', 'utf-8')

        subject = 'email test'
        msg['Subject'] = Header(subject, 'utf-8')
        try:
            smtp_obj = smtplib.SMTP_SSL(self.mail_host, 465)  # 服务器和端口号
            smtp_obj.login(self.sender, self.mail_password)
            smtp_obj.sendmail(self.sender, self.receivers, msg.as_string())
            smtp_obj.quit()
            print('send succeed')
        except smtplib.SMTPException as e:
            print('send fail' + e)


if __name__ == '__main__':
    mail = Mail()
    mail.send()
