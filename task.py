#!/usr/bin/env python
#coding:utf8

'''
Module Name: task.py
Author: zhanghai
Created: 2016-03-18
Last Modified:
Version: 1.0
Description: get urls and download images
'''

import threading
import time


class UrlThread(threading.Thread):
    '''get image links from each page'''
    def __init__(self, func):
        threading.Thread.__init__(self) 
        self.func = func

    def run(self):
        while True:
            time.sleep(1)
            self.func()


class DownloadThread(threading.Thread):
    '''download images '''
    def __init__(self, func):
        threading.Thread.__init__(self) 
        self.func = func

    def run(self):
        while True:
            time.sleep(1)
            self.func()
        

