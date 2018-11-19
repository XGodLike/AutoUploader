#__author__ = 'Administrator'
import py2exe
from distutils.core import setup

setup(console=['VrAutoUploader.py'],
      data_files = [('config',['config/VrAutoUploader.xml'])])