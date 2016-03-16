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

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")    

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
                pageLinks.append(pageLink)
            return pageLinks
        else:
            return None

def get_page_links2(pageLink):
    print "Starting to crawl : %s" %pageLink
    if pageLink:
        picture_urls = []  
        response = requests.get(pageLink) 
        soup = BeautifulSoup(response.text, "html.parser")
        picture_divs = soup.find_all("div", {"class":"pic"})
        for picture_div in picture_divs:
            picture_url = picture_div.find("a").get("href")
            picture_urls.append(picture_url)
        return picture_urls
    else:
        return None

def download_images(images_url):
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
                with open(os.path.join(DOWNLOAD_DIR, image_name), "wb") as fd:
                    for chunk in r.iter_content():
                        fd.write(chunk)
                print "%s has been downloaded" %image_name
            else:
                return None
            
    
if __name__ == "__main__":
    webUrl = "http://www.meizitu.com"
    pageLinks = get_page_links1(webUrl)
    htmlUrl = "http://www.meizitu.com/a/list_1_1.html"
    page_link = "http://www.meizitu.com/a/5328.html"
    for pageLink in pageLinks:
        image_urls = get_page_links2(pageLink)
        for image_url in image_urls:
            download_images(image_url)


    
