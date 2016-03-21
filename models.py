#!/usr/bin/env python
#coding:utf8

'''
    Dscription: sql api
    Script Name: db.py
    Author: zhanghai
    Created: 2016-03-21
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, 
    Column, 
    Integer, 
    String, 
    MetaData, 
    ForeignKey)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from config import SQLALCHEMY_DATABASE_URI
import datetime

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
BaseModel = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))
session = Session()


def init_db():
    BaseModel.metadata.create_all(engine)

def drop_db():
    BaseModel.metadata.drop_all(engine)


class FirstLevelLinks(BaseModel):
    __tablename__ = 'first_level_links' 

    id = Column(Integer, primary_key=True, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return "%s" %self.url


class SecondLevelLinks(BaseModel):
    __tablename__ = 'second_level_links' 

    id = Column(Integer, primary_key=True, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return "%s" %self.url


class ImageInfo(BaseModel):
    __tablename__ = 'image_information'

    id = Column(Integer, primary_key=True, nullable=False)
    md5 = Column(String)
    name = Column(String)
    first_level_link_id = Column(String, ForeignKey('first_level_links.id'))
    second_level_link_id = Column(String, ForeignKey('second_level_links.id'))
    created = Column(TIMESTAMP, default=datetime.datetime.now())
    updated = Column(TIMESTAMP)
    
    def __repr__(self):
        return "<Metadata('%s')>" %(self.name,)


if __name__ == "__main__":
    init_db()
    imageinfo = ImageInfo(md5='1234', name='1.jpg')
    #imageinfo.md5 = '1234'
    #imageinfo.name = '1.jpg'
    session.add(imageinfo)
    session.flush()
    session.commit()
