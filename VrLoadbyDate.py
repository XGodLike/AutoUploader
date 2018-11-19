#__author__ = 'Administrator'

import os
import time
from  datetime import datetime,timedelta


class LostDate():
    def __init__(self,dlog,dateformat):
        self.LostDateList = []
        self.__dateLog = dlog
        self.__dateFormat =dateformat

    def getDateList(self):
        self.LostDateList = []
        if not os.path.exists(self.__dateLog) or os.path.getsize(self.__dateLog) == 0:
            now = datetime.now().strftime(self.__dateFormat)
            now_struct = datetime.strptime(now,self.__dateFormat)+ timedelta(days=-1)
            now = now_struct.strftime(self.__dateFormat)
            self.LostDateList.append(now)
            return

        date_list = []
        with open(self.__dateLog,'r') as rf:
            line = rf.readline().replace('\n','')
            while line:
                #time_struct = time.strptime(line,self.__dateFormat)
                #new_format = time.strftime('%Y%m%d',time_struct)
                date_list.append(line)
                line = rf.readline().replace('\n','')

        time_struct = time.strptime(date_list[-1],self.__dateFormat)
        new_format = time.strftime('%Y%m%d',time_struct)
        latestDate = int(new_format)
        #latestDate = date_list[-1]
        Difdate = int(datetime.now().strftime('%Y%m%d')) - int(latestDate)
        for index in range(1,Difdate):
            date_str = str(latestDate + index)
            time_struct = time.strptime(date_str,'%Y%m%d')
            new_format = time.strftime(self.__dateFormat,time_struct)
            self.LostDateList.append(new_format)
            #self.LostDateList.append(int(latestDate)+index)

    def writeDateLog(self,Datelist):
         with open(self.__dateLog,'w') as wf:
            for dt in Datelist:
                wf.writelines(str(dt) + '\n')
                wf.flush()

    def setDateList(self,Datelist):
         self.LostDateList = Datelist


if __name__ == '__main__':
    m_l = LostDate('log.log','%Y-%m-%d')
    m_l.getDateList()
    print m_l.LostDateList