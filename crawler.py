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
from multiprocessing import Pool, Process
import signal
import sys
import logging
from task import UrlThread, DownloadThread
from config import *
from utils import create_md5
from models import (init_db, session, ImageInfo,\
    FirstLevelLinks, SecondLevelLinks)

logger = logging.getLogger(__name__)


def get_page_links1(webUrl):
    '''
        Description: get images' links
    '''
    init_db()
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
            for index in xrange(1, pageNumber+1):
                pageLink = "%s"*4 %(webUrl, m.group(1), index, m.group(3))
                #pageLinks.append(pageLink)
                page_link1_queue.put(pageLink)
                query = session.query(FirstLevelLinks)
                query_result = query.filter(FirstLevelLinks.url==pageLink).first()
                if query_result:
                    continue 
                else:
                    first_level_links = FirstLevelLinks(url=pageLink)
                    session.add(first_level_links)
            session.flush()
            session.commit()
            return page_link1_queue
        else:
            return None

def get_page_links2():
    pageLink = page_link1_queue.get()
    print "page links2 process id:%s" %os.getpid()
    print "Starting to crawl : %s" %pageLink
    if pageLink:
        #picture_urls = []  
        response = requests.get(pageLink) 
        soup = BeautifulSoup(response.text, "html.parser")
        picture_divs = soup.find_all("div", {"class":"pic"})
        for picture_div in picture_divs:
            picture_url = picture_div.find("a").get("href")
            page_link2_queue.put(picture_url)
            #picture_urls.append(picture_url)

            query = session.query(SecondLevelLinks)
            query_result = query.filter(SecondLevelLinks.url==picture_url).first()
            if query_result:
                continue
            else:
                second_level_links = SecondLevelLinks(url=picture_url)
                session.add(second_level_links)
        session.flush()
        session.commit()

        return page_link2_queue
    else:
        return None

def link2_middleware():
    '''middleware for get link of images html'''
    print '**************link2_middleware*************'
    while 1:
        time.sleep(1)
        get_page_links2()

def download_images():
    print "download process id: %s" %os.getpid()
    images_url = page_link2_queue.get()
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

                fname = os.path.join(DOWNLOAD_DIR, image_name)

                md5 = create_md5(fname) #create md5 for picture
                query_result = session.query(ImageInfo).filter_by(md5=md5).all()
                if not query_result:
                    #link1_id = session.query(FirstLevelLinks).filter(FirstLevelLinks.url==page_link).first().id
                    link2_id = session.query(SecondLevelLinks).filter(SecondLevelLinks.url==images_url).first().id

                    image_info = ImageInfo(name=image_name, md5=md5, url=image_source, second_level_link_id=link2_id)
                    session.add(image_info)
                    session.flush()
                    session.commit()
                    
                #download images
                if not os.path.exists(fname):
                    with open(fname, "wb") as fd:
                        for chunk in r.iter_content():
                            fd.write(chunk)
                    print "%s has been downloaded." %image_name

                else:
                    print "%s already exists." %image_name
                        
                    continue
            else:
                return None


def download_middleware():
    '''middleware for download images'''
    print '***********download_middleware***********'
    while 1:
        time.sleep(1)
        download_images()


def thread_task():
    '''
    pageLinks = get_page_links1(HOST)
    for index in xrange(len(pageLinks)):
        print "Starting to crawl page: %s" %(index+1)
        image_urls = get_page_links2(pageLinks[index])
        for image_url in image_urls:
            download_images(image_url)
    '''

    for i in xrange(THREAD_NUM):
        url_thread = UrlThread(get_page_links2)
        url_thread.setDaemon(True)
        url_thread.start()

    for i in xrange(THREAD_NUM):
        download_thread = DownloadThread(download_images)
        download_thread.setDaemon(True)
        download_thread.start()

    for i in xrange(THREAD_NUM):
        url_thread.join()

    for i in xrange(THREAD_NUM):
        download_thread.join()
        

def process_task():
    '''
    subprocess for crawl_main
    '''
    try:
        get_page_links1(HOST)

        '''
        processes = []
        for i in xrange(PROCESS_NUM):
            download_process = Process(target=download_images)
            download_process.start()
            processes.append(download_process)

        for p in processes:
            p.join()

        pool1 = Pool(PROCESS_NUM)
        for i in xrange(PROCESS_NUM):
            pool1.apply_async(link2_middleware)

        pool2 = Pool(PROCESS_NUM)
        for i in xrange(PROCESS_NUM):
            pool2.apply_async(download_middleware)

        pool1.close()
        pool1.join()
        pool2.close()
        pool2.join()
        '''

        pool = Pool(PROCESS_NUM)
        for i in xrange(PROCESS_NUM):
            pool.apply_async(thread_task)
        pool.close()
        pool.join()

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


