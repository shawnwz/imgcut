#! /usr/bin/python
# -*- coding: utf-8 -*-

######################################
#gaopin read excel into import_images table
#coding licl
#20141201 
#beijing
######################################

import MySQLdb, sys, traceback, time, datetime, types

import GpLog, GpUtils

class GpConfig:
	######################### manual begin ###############
	####mysql db config
	host = '123.57.62.143'
	port = 3306
	user = 'root'
	pw   = 'Gaopin2015'
	db   = 'gaopin_images'

	#####mongo config 
	serverUrl  = 'mongodb://192.168.1.21:27017'
	mongoUser  = 'gpImage'
	mongoPassw = '_gpImage'

	mongoAdminUser  = 'gaopin'
	mongoAdminPassw = 'gaopin@2014'

	#####solr config
	solrHost = '192.168.1.21'
	solrPort = 8080
	solrPath = path='/solr/images1/update?stream.body=<delete%20fromPending="false"%20fromCommitted="true"><id>{0}</id></delete>'

	desStorageId = '3'
	remark = 'tommy'
	status = '2'
	######################### manual end ###############

	#######const
	orgi_table = 'orgi_images'
	imp_table  = 'import_images'

	#####config file name
	impCfgFile = './col_i.cfg'
	orgiCfgFile = './col_o.cfg'
	########excel col name
	enKeyName = 'keyEnglish'
	cnKeyName = 'keyChinese'

	def __init__(self):
		pass

	def __del__(self):
		pass
