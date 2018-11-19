#__author__ = 'Administrator'
#coding:utf-8
import os
from VrLog import logger
import copy
import time
from  datetime import datetime
import paramiko


class Sftp_Upload():

    def __init__(self,host,port,username,password):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password

        self.__logger = None
        self.__sftp = None
        self.__remote_path = None
        self.__stopTime = None

        self.upload_flag = False     #上传是否成功
        self.zip_dict = {}           #待上传的zip包
        self.zip_counts = 0
        self.datelist = []           #最近的上传成功的
        #self.upload_counts = 0       #上传成功的文件总数

    def setLogger(self,logger):
        self.__logger = logger

    def setStopTime(self,st):
        self.__stopTime = st

    def setLocalPath(self,zip_dict):
        self.zip_dict = zip_dict

    def setRemote(self,remote):
        self.__remote_path =  remote

    def __login(self):
        if self.__sftp != None or \
            self.__host == None or \
            self.__port == None or \
            self.__username == None or\
            self.__password == None:
            return
        else:
            try:
                tf = paramiko.Transport((self.__host,self.__port))
                tf.connect(username=self.__username,password=self.__password)
                self.__sftp = paramiko.SFTPClient.from_transport(tf)
            except Exception,e:
                self.__logger.log_info('Upload:SFTP服务器连接失败:%s' % e)
                print 'Upload:SFTP Server connect unsuccessful:%s' % e

    def closeSftp(self):
        if self.__sftp:
            self.__sftp.close()
            self.__sftp = None

    def uploadFile(self,local_path,remote_path):
        if not os.path.isfile(local_path):
            self.__logger.log_info('Upload:应该上传单个文件')
            print 'Upload:local_path should be single file'
            return
        if not os.path.exists(local_path):
            self.__logger.log_info('Upload:本地文件不存在')
            print 'Upload:local file dont exist'
            return

        basename = os.path.basename(local_path)
        dir_list = self.__sftp.listdir()
        if basename in dir_list:
            self.__logger.log_info('Upload:%s 文件已经存在，跳过' % local_path)
            print 'Upload:%s file exited,jump' % local_path
            return

        pos = local_path.rfind('\\')
        remote_path += local_path[pos+1:len(local_path)]
        try:
            self.__sftp.put(local_path,remote_path)
            self.upload_flag = True
            self.__logger.log_info('Upload:%s 文件上传成功-->%s' % (local_path,remote_path))
            print 'Upload:%s upload successful-->%s' % (local_path,remote_path)
        except Exception,e:
            self.upload_flag = False
            self.__logger.log_info('%s 文件上传失败:%s'% (local_path,e))
            print '%s upload unsuccessful:%s'% (local_path,e)

    def upload(self):
        self.datelist = []
        while self.__sftp == None:
            self.__login()

        if self.__logger == None:
            self.__logger = logger('default_log')

        #设置上传截止时间,默认是06:00:00
        if self.__stopTime == None:
            self.setStopTime(6)

        if not self.zip_dict:
            self.__logger.log_info('Upload:待上传压缩文件为空')
            print 'Upload:uploading zip file is empty'
            return

        if self.__remote_path == None:
            self.__logger.log_info('Upload:sftp服务器路径未设置')
            print 'Upload:sftp server path dont seted'
            return

        try:
            self.__sftp.chdir(self.__remote_path)
        except:
            self.__sftp.mkdir(self.__remote_path)
            self.__sftp.chdir(self.__remote_path)

        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            now_time = time.strptime(now,'%Y-%m-%d %H:%M:%S')
            now_sec = time.mktime(now_time)
            stop_time = time.strptime(self.__stopTime,'%Y-%m-%d %H:%M:%S')
            stop_sec = time.mktime(stop_time)
            for dk in sorted(self.zip_dict.keys()):
                self.yesterday_list = copy.deepcopy(self.zip_dict[dk])
                for index in range(len(self.zip_dict[dk])):
                    if now_sec <= stop_sec:
                        self.uploadFile(self.zip_dict[dk][index],self.__remote_path)
                        self.yesterday_list.remove(self.zip_dict[dk][index]) #上传成功。删除
                        os.remove(self.zip_dict[dk][index])
                    else:
                        self.upload_flag = False
                        return
                if not self.yesterday_list:#已经全部上传完成，清空之后，在字典中删除key
                    self.zip_dict.pop(dk)
                    self.datelist.append(dk)
            self.upload_flag = True
        except Exception,e:
            self.__logger.log_info('Upload:上传出现异常:%s' % e)
            print 'Upload:upload except:%s' % e
            self.upload_flag = False

#模块测试
if __name__ == '__main__':
    remote = '/TMP/'
    Time = datetime.now().strftime('%Y%m%d')
    remote += str(Time) + '/'



    from VrLoadbyDate import LostDate
    m_lostDate = LostDate('datelog.log','%Y%m%d')
    m_lostDate.getDateList()

    from VrZip import File_Zip
    local_path = 'E:\\GetMovie-master\\VrAutoUploader\\2018\\'
    remote_path = 'E:\\GetMovie-master\\VrAutoUploader\\2018\\TEMP\\'
    file_zip = File_Zip(local_path,remote_path,'%Y%m%d','SZ')
    file_zip.setLostDate(m_lostDate.LostDateList)
    file_zip.MutilZip()

    print 'Zip Done'
    print file_zip.zip_dict

    sf = Sftp_Upload('mftqa.saic-gm.com',52022,'vcyber2nile','Rebycv1234')
    sf.setLocalPath(file_zip.zip_dict)
    sf.setRemote(remote)
    stop_time = datetime.now().strftime('%Y-%m-%d 23:00:00')
    sf.setStopTime(stop_time)
    sf.upload()
    sf.closeSftp()
    print sf.datelist
    print 'upload Done'










