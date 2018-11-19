#__author__ = 'Administrator'
#coding:utf-8

import cgi
import smtplib
import VrConfigParser
from VrLog import logger
from email.mime.text import MIMEText



class Send_Email():
    def __init__(self,mail_info = {}):
        self.__logger = None
        self.__mail_info = mail_info
        self.__BeSendEmail = True   #发送邮件的开关
        self.__receivers = None
        self.__sender = None
        self.__sender_pwd = None
        self.__subject = None
        self.__smtpserver = None

        self.__content = None

    def __getEmailInfo(self):
        self.__receivers = self.__mail_info['Recviers']
        self.__sender = self.__mail_info['Sender']
        self.__sender_pwd = self.__mail_info['Mailpwd']
        self.__smtpserver = self.__mail_info['SmtpServer']
        self.__subject = self.__mail_info['Mailsubjcet']
        self.__BeSendEmail = self.__mail_info['Besend']

    def setLogger(self,logger):
        self.__logger = logger


    def setcontent(self,time,content,file_counts,zip_counts,remote_path,stime,etime,unsucess_counts,reason):
        sucess_counts = zip_counts - unsucess_counts
        self.__content = '\nTime：%s\n数据内容：%s\n文件总数：%d\n压缩文件总数：%d\n上传路径：%s\n同步开始时间：%s\n同步结束时间：%s\n成功上传压缩文件：%d个\n失败：%d个\n\n失败原因：%s' % \
                (time,content,file_counts,zip_counts,remote_path,stime,etime,sucess_counts,unsucess_counts,reason)

    def send_email(self):
        if self.__mail_info == {}:
            self.__logger.log_info('邮件配置解析有误')
            print 'mail parser failed'
            return
        self.__getEmailInfo()
        #是否发送邮件的开关
        if not self.__BeSendEmail:
            return
        if self.__logger == None:
            self.__logger = logger('default_log')

        if self.__receivers == None or self.__sender == None:
            self.__logger.log_info('Email:地址缺失')
            print 'Email:adress lost'
            return
        if self.__content == None:
            self.__logger.log_info('Email:内容缺失')
            print 'Email:contentlost '
            return
        body = '''<!doctype html>
        <html>
        <head>
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=7" />
        <title>%s</title>
        </head>
        <body>
        <pre style="font-family:楷体;font-size:18px">
        %s
        </pre>
        </body>
        </html>
        ''' % (self.__subject.encode('utf-8'), cgi.escape(self.__content))
        msg = MIMEText(body, 'html', 'utf-8')
        msg['Subject'] = self.__subject
        msg['From'] = self.__sender
        msg['To'] = self.__receivers

        try:
            smtpObj = smtplib.SMTP(self.__smtpserver,25)
            smtpObj.login(self.__sender, self.__sender_pwd)
            smtpObj.sendmail(self.__sender, self.__receivers.split(','), msg.as_string())
            self.__logger.log_info('Email:邮件发送成功')
            print 'Email:send email successful'
        except Exception,e:
            self.__logger.log_info('Email:邮件发送失败:%s' % e)
            print 'Email:send email unsuccessful:%s' % e


if __name__ == '__main__':
    print 1
    # s_mail = Send_Email()
    # s_mail.setcontent(None,None,0,None,None,0,None)
    # s_mail.send_email()
