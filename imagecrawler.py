#!/usr/bin/env python
#coding:utf8

'''
Script Name: imagecrawler.py
Author: zhanghai
Created: 2016-03-15
Last Modified: 
Version: 1.0
Description: crawl images from Internet
'''

import requests
from bs4 import BeautifulSoup
import re


def get_urls(webUrl):
    '''
    Description: get images' url
    '''
    print webUrl
   

if __name__ == "__main__":
    webUrl = "http://www.meizutu.com"
    urlList = get_urls(webUrl)

    
