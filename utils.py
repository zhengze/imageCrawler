#!/usr/bin/env python
#coding:utf8

#Script Name: utils.py
#Author: zhanghai
#Date: 2016-03-21

import hashlib
from config import SECRET_KEY

def create_md5(image_file):
    try:
        f = open(image_file,  'rb').read()   
        hash_string = hashlib.md5(f).hexdigest()
        return hash_string
    except Exception, e:
        raise
        return None
        
        
         
        
    
