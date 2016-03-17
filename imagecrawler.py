#!/usr/bin/env python
#coding:utf8

'''
Script Name: imagecrawler.py
Author: zhanghai
Created: 2016-03-15
Last Modified: 
Version: 1.0
Description: crawl images from http://wwww.meizitu.com
'''

import requests
from bs4 import BeautifulSoup
import re
import os
import time
from multiprocessing import Pool, Process, Queue, Manager
import signal
import sys

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")    
HOST = "http://www.meizitu.com"
PROCESS_NUM = 2

manager = Manager()
page_link1_queue = manager.Queue()
page_link2_queue = manager.Queue()
download_queue = manager.Queue()


def get_page_links1(webUrl):
    '''
        Description: get images' links
    '''
    webList = []
    htmlContent = requests.get(webUrl)
    soup = BeautifulSoup(htmlContent.text, "html.parser")
    wp_page_numbers_div = soup.find("div", {"id":"wp_page_numbers"})
    endPageTag = wp_page_numbers_div.find_all("a")[-1]
    endPageLink = endPageTag.get('href')
    if endPageLink: 
        regex = r"(\D+\d+\D+)(\d+)(\D+)"
        m = re.match(regex, endPageLink)
        if m:
            pageNumber = int(m.groups()[1])  #get page number
            pageLinks = []
            for index in xrange(1, pageNumber+1):
                pageLink = "%s"*4 %(webUrl, m.group(1), index, m.group(3))
                #pageLinks.append(pageLink)
                page_link1_queue.put(pageLink)
            return page_link1_queue
        else:
            return None

def get_page_links2():
    pageLink = page_link1_queue.get()
    print "Starting to crawl : %s" %pageLink
    if pageLink:
        picture_urls = []  
        response = requests.get(pageLink) 
        soup = BeautifulSoup(response.text, "html.parser")
        picture_divs = soup.find_all("div", {"class":"pic"})
        for picture_div in picture_divs:
            picture_url = picture_div.find("a").get("href")
            #picture_urls.append(picture_url)
            page_link2_queue.put(picture_url)
        return page_link2_queue
    else:
        return None

def download_images():
    images_url = page_link2_queue.get()
    print "download process id: %s" %os.getpid()
    print "Starting to crawl : %s" %images_url
    if images_url:
        response = requests.get(images_url)
        soup = BeautifulSoup(response.text, "html.parser")
        image_div = soup.find("div", {"id":"picture"})
        image_links = image_div.find_all("img")
        images_names = []
        for image_link in image_links:
            image_source = image_link.get("src")
            regex = r"(\D+)(\d+)(\D+)(\d+)(\D+)(\d+)(\D+)(\d+)(\D+)"
            m = re.match(regex, image_source)
            if m:
                image_name = "%s_%s_%s_%s%s" %(m.group(2), m.group(4), \
                    m.group(6), m.group(8), m.group(9)) 
                r = requests.get(image_source, stream=True)

                #download images
                fname = os.path.join(DOWNLOAD_DIR, image_name)
                if not os.path.exists(fname):
                    with open(fname, "wb") as fd:
                        for chunk in r.iter_content():
                            fd.write(chunk)
                    print "%s has been downloaded" %image_name
                else:
                    continue
            else:
                return None

def crawl_main():
    pageLinks = get_page_links1(HOST)
    time.sleep(1)   
    for index in xrange(len(pageLinks)):
        print "Starting to crawl page: %s" %(index+1)
        image_urls = get_page_links2(pageLinks[index])
        for image_url in image_urls:
            download_images(image_url)

def process_task():
    '''
    subprocess for crawl_main
    '''
    try:
        get_page_links1(HOST)

        link2_process = Process(target=get_page_links2)
        link2_process.start()
        link2_process.join()

        '''
        processes = []
        for i in xrange(PROCESS_NUM):
            download_process = Process(target=download_images)
            download_process.start()
            #download_process.join()
            processes.append(download_process)


        for p in processes:
            p.join()

        pool1 = Pool(2)
        for i in xrange(2):
            pool1.apply_async(get_page_links2)
        pool1.close()
        pool1.join()
        '''


        pool2 = Pool(2)
        for i in xrange(2):
            pool2.apply_async(get_page_links2)
        pool2.close()
        pool2.join()

        print 'All work done.'
    except KeyboardInterrupt:
        sys.exit(0)
    

if __name__ == "__main__":
    signal.signal(signal.SIGINT, process_task)
    signal.signal(signal.SIGTERM, process_task)

    start = time.time()

    process_task()

    end = time.time()
    running_time = end - start
    print "The programe's running time:%s" %running_time


