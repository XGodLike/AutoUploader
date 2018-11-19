#__author__ = 'Administrator'

from ConfigParser import ConfigParser

class config_parser():
    def __init__(self,config_path):
        self.__config = ConfigParser()
        self.__path = config_path
        self.info = {}

    def parser(self):
        self.__config.read(self.__path)
        for section in self.__config.sections():
            self.info[section] = {}
            for option in self.__config.options(section):
                self.info[section][option] = self.__config.get(section,option)

if __name__ == '__main__':
    con = config_parser('VrConfig.ini')
    con.parser()
    print con.info
    for key in con.info.keys():
        print key
        for k in con.info[key].keys():
            print '{0}={1}'.format(k,con.info[key][k])