#__author__ = 'Administrator'
#coding:utf-8
import os
import copy
from VrLog import logger
import czipfile
from VrLoadbyDate import LostDate
from datetime import datetime,timedelta



PER_DISK_OF_ZIP = 1024 * 1024 * 64


file_size = 0
zip_index = 1

class File_Zip():

    def __init__(self,file_path,temp_path,file_name,fileFomat,data_city=None):
        self.__city = data_city
        self.__rootpath = file_path     #待压缩文件的文件夹
        self.__path = None              #待压缩文件夹的下一级目录(加上日期)
        self.__zip_file = None
        self.__temp_path = temp_path    #临时文件夹
        self.__logger = None            #日志文件
        #self.__fileFomat = fileFomat   #日期文件格式
        self.__lostDate = None          #包括几天的待压缩文件，为None的话就只压缩昨天的;[20180408,20180409]
        self.__date = None
        self.__file_name=file_name      #压缩文件名

        self.zip_flag = False       #压缩是否完成
        self.filecount = 0          #所有文件夹中的文件总数

        self.filelist = []          #所有待压缩文件夹,分包压缩成多个文件
        self.zip_dict = {}          #生成的压缩文件列表;{20180408:['x-1.zip','x-2.zip'],20180409:['y-1.zip','y-2.zip]}

    def setLostDate(self,datelist):
        self.__lostDate  = datelist

    def setLogger(self,logger):
        self.__logger = logger

    # def setTmpPath(self,path):
    #     self.__temp_path = path + datetime.now().strftime(self.__fileFomat)

    #初始化时候只上传昨天日期的文件夹
    # def getYesterday(self,fileFomat):
    #     today = datetime.today()
    #     oneday = timedelta(days=1)
    #     yesterday = today - oneday
    #     self.__yesterday = str(yesterday.strftime(fileFomat))

    #首次启动，只上传昨天的数据
    def getFiles(self,path):
        for root,dirnames,filenames in os.walk(path):
            fpath = root.replace(path,'')
            fpath = fpath and fpath + os.sep or os.sep
            for filename in filenames:
                self.filecount += 1
                self.filelist.append(fpath+filename)


    def getMutilZip(self):
        global file_size
        global zip_index

        file_size = 0
        dateziplist = []
        if not os.path.exists(self.__temp_path + str(self.__date)+"/"):
            os.makedirs(self.__temp_path+ str(self.__date)+"/")
        if self.filelist:
            zip_logname = '{0}-{1}.log.zip'.format(self.__temp_path + str(self.__date)+"\\"+self.__file_name,str(zip_index))
            zip_wavname = '{0}-{1}.wav.zip'.format(self.__temp_path + str(self.__date)+"\\"+self.__file_name,str(zip_index))
            self.zip_log = czipfile.ZipFile(zip_logname,'w',czipfile.ZIP_DEFLATED)
            self.zip_wav = czipfile.ZipFile(zip_wavname,'w',czipfile.ZIP_DEFLATED)
            if self.zip_log:
                dateziplist.append(zip_logname)
            if self.zip_wav:
                dateziplist.append(zip_wavname)
            for file in self.filelist:
                file_size += os.path.getsize(self.__path+file)
                if file.rfind(".log")>0:
                    if file_size <= PER_DISK_OF_ZIP:
                        self.zip_log.write(self.__path+file,file)
                    else:
                        self.__logger.log_info('Zip:%s 压缩完成' % zip_logname)
                        print 'Zip:%s done' % zip_logname
                        self.zip_log.close()
                        file_size = 0
                        zip_index += 1
                        zip_logname = '{0}-{1}.log.zip'.format(self.__temp_path + str(self.__date)+"\\"+self.__file_name,str(zip_index))
                        self.zip_log = czipfile.ZipFile(zip_logname,'w',czipfile.ZIP_DEFLATED)
                        if self.zip_log:
                            dateziplist.append(zip_logname)
                elif file.rfind(".wav")>0:
                    if file_size <= PER_DISK_OF_ZIP:
                        self.zip_wav.write(self.__path+file,file)
                    else:
                        self.__logger.log_info('Zip:%s 压缩完成' % zip_wavname)
                        print 'Zip:%s done' % zip_wavname
                        self.zip_wav.close()
                        file_size = 0
                        zip_index += 1
                        zip_wavname = '{0}-{1}.wav.zip'.format(self.__temp_path + str(self.__date)+"\\"+self.__file_name,str(zip_index))
                        self.zip_wav = czipfile.ZipFile(zip_wavname,'w',czipfile.ZIP_DEFLATED)
                        if self.zip_wav:
                            dateziplist.append(zip_wavname)
            if file_size != 0:
                self.__logger.log_info('Zip:%s 压缩完成' % zip_logname)
                print 'Zip:%s done' % zip_logname
                self.__logger.log_info('Zip:%s 压缩完成' % zip_wavname)
                print 'Zip:%s done' % zip_wavname
            self.zip_log.close()
            self.zip_wav.close()
            self.zip_dict[self.__date] = copy.deepcopy(dateziplist)
        else:
            return


    #按包压缩，先将要压缩的文件区分好
    def MutilZip(self):
        global zip_index

        if self.__logger == None:
            self.__logger = logger('default_log')
        try:
            if not self.__lostDate:
                self.__logger.log_info('Zip:没有需要压缩的文件')
                print 'Zip:no zip need'
            else:
                print 'Zip:zip is starting'
                for dt in self.__lostDate:
                    zip_index = 1
                    self.__date = dt
                    self.__path = self.__rootpath + str(dt)
                    if not os.path.exists(self.__path):
                        self.__logger.log_info('Zip:%s 文件夹数据不存在' % self.__path.encode('utf-8'))
                        print 'Zip:%s dont exist ' % self.__path
                        continue
                    self.filelist = []
                    self.getFiles(self.__path)
                    self.__logger.log_info('Zip:%s 开始压缩文件' % self.__path.encode('utf-8'))
                    self.getMutilZip()
                    self.zip_flag = True
                self.__logger.log_info('Zip:压缩全部完成')
                print 'Zip:all zip done'
        except Exception,e:
            self.zip_flag = False
            self.__logger.log_info('Zip:压缩失败:%s' % e)
            print 'Zip:zip unsuccessful:%s'% e


#模块测试
if __name__ == '__main__':
    m_lostDate = LostDate('D:\\WorkSpace\\VrAutoUploader\\2018\\log\\date.log','%Y%m%d')
    m_lostDate.getDateList()

    local_path = 'D:\\WorkSpace\\VrAutoUploader\\2018\\NGI_v1.0\\'
    remote_path = 'D:\\WorkSpace\\VrAutoUploader\\2018\\TEMP\\VCYBER\\'
    file_name="ICI1.0-SHserver1"
    file_zip = File_Zip(local_path,remote_path,file_name,'%Y%m%d','SZ')
    file_zip.setLostDate(m_lostDate.LostDateList)
    file_zip.MutilZip()
    print 'Zip Done'
    print file_zip.zip_dict






