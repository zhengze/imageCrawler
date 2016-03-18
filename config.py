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
