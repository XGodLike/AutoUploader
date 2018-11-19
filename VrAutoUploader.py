#__author__ = 'Administrator'
#coding:utf-8

import os
import shutil
from VrLoadbyDate import LostDate
from VrXmlParser import Xml_Parser
from VrLog import logger
import time
import threading
from VrEmail import Send_Email
from VrZip import File_Zip
from VrUpload import Sftp_Upload
from datetime import datetime,timedelta


#时间间隔
ELAPSE_TIME = 3
#出现失败的情况
REASON = {'Done':'无异常','zip_ex':'压缩出现异常','No_file':'昨日无待上传的文件','over_load_time':'规定时间内上传未完成','up_ex':'上传出现异常','other':'其他'}

remote_path = None
ZIP_TIME = None
UPLOAD_TIME = None
STOP_TIME = None
temp_path=None

zip_time = None
upload_time = None
stop_time = None

L = threading.Lock() # 引入锁


class VrAutoUploader():

    def __init__(self,zip,sftp,email,lost,xml):
        self.__logger = None
        self.__etime = None     #上传结束时间
        self.__reason = None
        self.__init = True      #开启时候，不发送邮件

        self.zip = zip
        self.sftp_upload = sftp
        self.email = email
        self.lost_date = lost
        self.xml = xml

    #发送邮件
    def send_email(self):
        global remote_path
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yesterday_time = datetime.strptime(now,'%Y-%m-%d %H:%M:%S') + timedelta(days=-1)
        content = yesterday_time.strftime('%Y-%m-%d')
        unsuccessful_count = 0
        for index in self.sftp_upload.zip_dict.keys():
            unsuccessful_count += len(self.sftp_upload.zip_dict[index])
        if self.__etime != None:
            self.email.setcontent(now,content,self.zip.filecount,self.sftp_upload.zip_counts,remote_path,upload_time,self.__etime,unsuccessful_count,self.__reason)
            self.email.send_email()

    def setLogger(self,logger):
        self.__logger = logger

    #压缩状态需要重新初始化
    def initZipNextDay(self,next_day):
        self.zip.setLostDate(next_day)

    #上传状态需要重新初始化
    def initUploadNextDay(self,next_day):
        global remote_path
        global stop_time
        global temp_path

        #压缩状态初始化
        self.zip.zip_flag = False
        self.zip.filecount = 0
        temp_path = self.xml.zip_info['TempDir']

        #先将今天上传成功的日期列表写入日志文件中+
        self.lost_date.writeDateLog(self.sftp_upload.datelist)
        #上传状态需要重新初始化
        self.sftp_upload.upload_flag = False
        self.sftp_upload.zip_dict = {}
        self.sftp_upload.zip_counts = 0
        self.sftp_upload.datelist = []
        remote_path = self.xml.upload_info['SftpDir']
        remote_path = (remote_path + next_day + '/').encode('utf-8')
        self.sftp_upload.setRemote(remote_path)
        self.sftp_upload.setStopTime(stop_time)


        #直接将今天的日期传给self.lost_date.LostDateList
        self.lost_date.setDateList([int(datetime.now().strftime('%Y%m%d'))])

    #上传
    def fix_time_upload(self):
        global upload_time
        global stop_time
        global temp_path
        if self.__logger == None:
            self.__logger = logger('default_log')

        while True:
            #当前时间转换成‘时间戳’
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print '%s:%s' % (threading.currentThread().getName(),now)
            now_time = time.strptime(now,'%Y-%m-%d %H:%M:%S')
            now_sec = time.mktime(now_time)
            #开始上传时间转换成‘时间戳’
            s_time = time.strptime(upload_time,'%Y-%m-%d %H:%M:%S')
            s_sec = time.mktime(s_time)
            #最晚上传时间转换成‘时间戳’
            e_time = time.strptime(stop_time,'%Y-%m-%d %H:%M:%S')
            e_sec = time.mktime(e_time)
            if now_sec >= s_sec and now_sec <= e_sec:
                if self.zip.zip_dict and self.zip.zip_flag:
                    #获取待上传的所有压缩文件数目
                    for date_index in self.zip.zip_dict.keys():
                        self.sftp_upload.zip_counts += len(self.zip.zip_dict[date_index])
                    #待上传的所有压缩文件
                    self.sftp_upload.setLocalPath(self.zip.zip_dict)

                    print 'AutoUploader:start upload zipfiles'
                    self.__logger.log_info('AutoUploader:开始上传压缩文件')
                    self.sftp_upload.upload()
                else:
                    print u'AutoUploader:zip unfinished...standby'
                    self.__logger.log_info('压缩未完成,等待...')
                    self.sftp_upload.upload_flag = False

                if self.sftp_upload.upload_flag:
                    #一定记得关闭
                    self.sftp_upload.closeSftp()
                    self.__reason = REASON['Done']
                    self.__etime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if self.xml.mail_info['Besend'] != 0:
                        self.send_email()
                    upload_time = datetime.strptime(upload_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                    next_day = upload_time.strftime(self.xml.zip_info['DateFormat'])
                    upload_time = upload_time.strftime('%Y-%m-%d %H:%M:%S')
                    stop_time = datetime.strptime(stop_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                    stop_time = stop_time.strftime('%Y-%m-%d %H:%M:%S')
                    print 'AutoUploader:all zipfiles upload successful'
                    self.__logger.log_info('AutoUploader:压缩文件全部上传成功')
                    #为第二天的上传初始化
                    self.initUploadNextDay(next_day)
                    #删除空文件夹
                    for root,dirnames,filenames in os.walk(temp_path):
                        for FileDir in dirnames:
                            lstFile=os.listdir(temp_path+FileDir)
                            if lstFile==[]:
                                if os.path.exists(temp_path+FileDir):
                                    shutil.rmtree(temp_path+FileDir)
                time.sleep(ELAPSE_TIME)
            elif now_sec > e_sec:
                if not self.__init:
                    #一定记得关闭
                    self.sftp_upload.closeSftp()
                    if self.zip.filecount > 0:
                        self.__reason = REASON['over_load_time']
                        print 'AutoUploader:out of upload times'
                        self.__logger.log_info('AutoUploader:超出压缩文件上传时间段')
                    else:
                        self.__reason = REASON['No_file']
                        print 'AutoUploader:no file need uploaded'
                        self.__logger.log_info('AutoUploader:没有文件需要上传')
                    self.__etime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if self.xml.mail_info['Besend'] != 0:
                        self.send_email()

                self.__init = False
                upload_time = datetime.strptime(upload_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                next_day = upload_time.strftime(self.xml.zip_info['DateFormat'])
                upload_time = upload_time.strftime('%Y-%m-%d %H:%M:%S')
                stop_time = datetime.strptime(stop_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                stop_time = stop_time.strftime('%Y-%m-%d %H:%M:%S')


                self.initUploadNextDay(next_day)
                time.sleep(ELAPSE_TIME)
            else:
                time.sleep(ELAPSE_TIME)

    #压缩
    def fix_time_zip(self):
        global zip_time
        flag = 0
        while True:
            s_time = time.strptime(zip_time,'%Y-%m-%d %H:%M:%S')
            s_sec = time.mktime(s_time)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            now_time = time.strptime(now,'%Y-%m-%d %H:%M:%S')
            now_sec = time.mktime(now_time)
            print '%s:%s' % (threading.currentThread().getName(),now)
            if flag == 0:
                if now_sec >= s_sec:
                    self.zip.MutilZip()
                    flag = 1
                else:
                    time.sleep(ELAPSE_TIME)
            else:
                now_time = datetime.strptime(zip_time,'%Y-%m-%d %H:%M:%S')
                zip_time = datetime.strptime(zip_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=1)
                zip_time = zip_time.strftime('%Y-%m-%d %H:%M:%S')
                next_day = now_time.strftime(self.xml.zip_info['DateFormat'])
                self.initZipNextDay([next_day])
                flag = 0
                time.sleep(ELAPSE_TIME)


#两个线程
# 线程1：一个线程在每天凌晨00:03:00开始压缩前天的文件
# 线程2：一个线程在每天凌晨03:03:00开始上传压缩好的文件，首先判断前天上传是否有失败，有失败的先上传前天失败的，再上传今天的
def serviceStart():
    #日志模块
    log_path = 'E:\\GetMovie-master\\VrAutoUploader\\2018\\log'
    m_log = logger(log_path)
    m_log.setLogger()
    #邮件模块
    Email = Send_Email('VrConfig.ini')
    #压缩模块
    file_path = 'E:\\GetMovie-master\\VrAutoUploader\\2018\\'
    temp_path = 'E:\\GetMovie-master\\VrAutoUploader\\2018\\TEMP\\'
    file_name='ICI1.0-SHserver1'
    Zip = File_Zip(file_path,temp_path,'BJ')
    Zip.setLogger(m_log)

    #上传模块
    remote = '/TMP/'
    Time = datetime.now().strftime('%Y-%m-%d')
    remote += str(Time) + '/'
    Up_loader = Sftp_Upload('mftqa.saic-gm.com',52022,'vcyber2nile','Rebycv1234')
    Up_loader.setRemote(remote)
    Up_loader.setStopTime(stop_time)
    Up_loader.setLogger(m_log)
    v_A = VrAutoUploader(Zip,Up_loader,Email,log_path)
    v_A.setLogger(m_log)
    t1 = threading.Thread(target=v_A.fix_time_zip)
    t2 = threading.Thread(target=v_A.fix_time_upload)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def serviceStartWithXML(xml_path):
    global ZIP_TIME,UPLOAD_TIME,STOP_TIME,zip_time,upload_time,stop_time
    global remote_path,datelog_path

    #xml解析模块
    xml = Xml_Parser(xml_path)
    xml.xmlParser()

    #获取待上传文件的日期列表
    Lost_date = LostDate(xml.log_info['DateLogfile'],xml.zip_info['DateFormat'])
    Lost_date.getDateList()


    #重构时间串
    ZIP_TIME = '%Y-%m-%d ' + xml.zip_info['ZipTime']
    UPLOAD_TIME = '%Y-%m-%d '+ xml.upload_info['UploadTime']
    STOP_TIME = '%Y-%m-%d ' + xml.upload_info['UploadEndTime']

    zip_time = datetime.now().strftime(ZIP_TIME)        #压缩开始时间
    upload_time = datetime.now().strftime(UPLOAD_TIME)  #开始上传时间
    stop_time = datetime.now().strftime(STOP_TIME)      #上传的最晚时间

    #日志模块
    log_path = xml.log_info['Logfile']
    print(log_path)
    m_log = logger(log_path)
    m_log.setLogger()

    #邮件模块
    Email = Send_Email(xml.mail_info)
    Email.setLogger(m_log)

    #压缩模块
    file_path = xml.zip_info['dataDir']
    temp_path = xml.zip_info['TempDir']
    file_name = xml.zip_info['FileName']
    Zip = File_Zip(file_path,temp_path,file_name,xml.zip_info['DateFormat'],xml.zip_info['dataSuffix'])
    Zip.setLostDate(Lost_date.LostDateList)
    Zip.setLogger(m_log)

    #上传模块
    remote_path = xml.upload_info['SftpDir']
    Time = datetime.now().strftime(xml.zip_info['DateFormat'])
    remote_path = (remote_path + Time + '/').encode('utf-8')
    Up_loader = Sftp_Upload(xml.fstp_info['Host_name'],xml.fstp_info['Port'],xml.fstp_info['User_name'],xml.fstp_info['Password'])
    Up_loader.setRemote(remote_path)
    Up_loader.setStopTime(stop_time)
    Up_loader.setLogger(m_log)

    v_A = VrAutoUploader(Zip,Up_loader,Email,Lost_date,xml)
    v_A.setLogger(m_log)

    t1 = threading.Thread(target=v_A.fix_time_zip)
    t2 = threading.Thread(target=v_A.fix_time_upload)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
if __name__ == '__main__':
    #serviceStart()
    print 'AutoUploader start...'
    xml_path = '.\\config\\VrAutoUploader.xml'
    if os.path.exists(xml_path):
        serviceStartWithXML(xml_path)

