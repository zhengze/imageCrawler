#coding:utf8

#File Name: config.py
#Date time: 2016-03-18

import os
from multiprocessing import Manager

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")    
HOST = "http://www.meizitu.com"

THREAD_NUM = 2
PROCESS_NUM = 2

manager = Manager()
page_link1_queue = manager.Queue()
page_link2_queue = manager.Queue()

SECRET_KEY = 'm#ovtr^ax%n3)m$80s6-5x*$^3-izig&ghfccuohb5$(851l&s'

DATA_DIR = os.path.join(BASE_DIR, "data")
SQLALCHEMY_DATABASE_URI = "%s%s%s" %("sqlite:///", DATA_DIR, "/meizitu.db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, "db_repository")
