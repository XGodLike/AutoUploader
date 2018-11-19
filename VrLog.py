#__author__ = 'Administrator'
#coding:utf-8

import os
import time
import logging
from logging import handlers
from datetime import datetime

class logger:
    def __init__(self,path):
        self.__log_path = path
        self.__logger = None

    def setLogger(self):
        if not os.path.exists(self.__log_path):
            os.mkdir(self.__log_path)

        self.__logger = logging.getLogger("mylogger")
        log  = self.__log_path + '\\AutoUploader_log'
        handler = handlers.TimedRotatingFileHandler(log, 'H', 1, 24) #切割日志
        handler.suffix = "%Y-%m-%d_%H"#从源码可以看出必须是这个格式才会切割
        #format = logging.Formatter('[%(levelname)s][%(funcName)s][%(asctime)s]%(message)s')
        format = logging.Formatter('[%(levelname)s][%(asctime)s]%(filename)s:%(lineno)d]:%(message)s')
        handler.setFormatter(format)
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.INFO)
        #__logger.fatal(datetime.now().strftime('%Y-%m-%d')) #在新日志中写上当天的日期

    def log_info(self,info):
        if self.__logger == None:
            self.setLogger()
        self.__logger.info(info)


if __name__ == '__main__':

    log_path = 'D:\\WorkSpace\\VrAutoUploader\\2018\\log\\'
    m_log = logger(log_path)
    m_log.setLogger()
    while True:
        m_log.log_info('222')
        time.sleep(0.1)
