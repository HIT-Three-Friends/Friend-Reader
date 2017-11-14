#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser,logging

class basespider(object):

	def __init__(self):
		self.loadConfig()
		self.prepare()
	
	def loadConfig(self):
		self.socialRoot="./social/"
		#self.socialRoot="./"
		self.allConfig=configparser.ConfigParser(interpolation=None)
		self.allConfig.read(self.socialRoot+"config.properties",encoding='utf-8')
		try:
			self.spiderConfig=configparser.ConfigParser(interpolation=None)
			self.spiderConfig.read(self.socialRoot+"spider.properties",encoding='utf-8')
		except Exception as e:
			logging.info("spider.properties not exist, ignored")
			
		
	def prepare(self):
		logging.basicConfig(format='%(asctime)s --%(lineno)s -- %(levelname)s:%(message)s', level=logging.INFO)
