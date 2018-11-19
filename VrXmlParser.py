#__author__ = 'Administrator'
#coding:utf-8
from xml.dom.minidom import parse
import xml.dom.minidom


class Xml_Parser():
    def __init__(self,xmlfile):
        self.__xml = xmlfile
        self.fstp_info = {}
        self.mail_info = {}
        self.zip_info = {}
        self.upload_info = {}
        self.log_info = {}

    def xmlParser(self):
        dom = xml.dom.minidom.parse(self.__xml)
        elment = dom.documentElement
        Sftp = elment.getElementsByTagName('SftpServer')
        #fstpserver相关配置
        self.fstp_info['Host_name']= Sftp[0].getElementsByTagName('Host_name')[0].childNodes[0].data
        self.fstp_info['User_name']= Sftp[0].getElementsByTagName('User_name')[0].childNodes[0].data
        self.fstp_info['Password'] = Sftp[0].getElementsByTagName('Password')[0].childNodes[0].data
        self.fstp_info['Port'] = int(Sftp[0].getElementsByTagName('Port')[0].childNodes[0].data)
        #压缩模块相关配置
        zip = elment.getElementsByTagName('Zip')
        self.zip_info['dataSuffix']= zip[0].getElementsByTagName('dataSuffix')[0].childNodes[0].data
        self.zip_info['dataDir']= zip[0].getElementsByTagName('dataDir')[0].childNodes[0].data
        self.zip_info['TempDir']= zip[0].getElementsByTagName('TempDir')[0].childNodes[0].data
        self.zip_info['FileName']= zip[0].getElementsByTagName('FileName')[0].childNodes[0].data
        self.zip_info['DateFormat'] = zip[0].getElementsByTagName('DateFormat')[0].childNodes[0].data
        self.zip_info['ZipTime'] = zip[0].getElementsByTagName('ZipTime')[0].childNodes[0].data
        #上传模块相关配置
        upload = elment.getElementsByTagName('Upload')
        self.upload_info['SftpDir']= upload[0].getElementsByTagName('SftpDir')[0].childNodes[0].data
        self.upload_info['UploadTime']= upload[0].getElementsByTagName('UploadTime')[0].childNodes[0].data
        self.upload_info['UploadEndTime'] = upload[0].getElementsByTagName('UploadEndTime')[0].childNodes[0].data
        #日志模块相关配置
        log = elment.getElementsByTagName('Log')
        self.log_info['Logfile']= log[0].getElementsByTagName('Logfile')[0].childNodes[0].data
        self.log_info['DateLogfile']= log[0].getElementsByTagName('DateLogfile')[0].childNodes[0].data
        #邮件模块相关配置
        mail = elment.getElementsByTagName('Mail')
        self.mail_info['Besend']= int(mail[0].getElementsByTagName('Besend')[0].childNodes[0].data)
        self.mail_info['Recviers']= mail[0].getElementsByTagName('Recviers')[0].childNodes[0].data
        self.mail_info['Sender']= mail[0].getElementsByTagName('Sender')[0].childNodes[0].data
        self.mail_info['Mailpwd']= mail[0].getElementsByTagName('Mailpwd')[0].childNodes[0].data
        self.mail_info['SmtpServer']= mail[0].getElementsByTagName('SmtpServer')[0].childNodes[0].data
        self.mail_info['Mailsubjcet']= mail[0].getElementsByTagName('Mailsubjcet')[0].childNodes[0].data


if __name__ == '__main__':
    m_xml = Xml_Parser('E:\\GetMovie-master\\VrAutoUploader\\VrAutoUploader.xml')
    m_xml.xmlParser()
    print m_xml.fstp_info
    print m_xml.mail_info
    print m_xml.zip_info
    print m_xml.upload_info
    print m_xml.log_info

