#! /usr/bin/python
# -*- coding: utf-8 -*-
 
######################################
#gaopin proc mongodb
#coding licl
#20141208
#chengdu
######################################

import pymongo

import GpLog, GpUtils
from GpConfig import GpConfig

class MongoDao:
	conn = None	
	#database
	imageDb = None
	#table
	imageMeta = None
	imageConfig = None
	imageExcel = None
	cutCorbisId = None
	errorCorbisId = None
	cutedCorbisId = None
	cutErrorMsg = None
	delCorbisId = None
	reCutCorbisId = None
	impErrorMsg = None
	

	config = GpConfig()

	##
	#db.imageMeta.drop()
	#db.imageConfig.drop()
	#db.imageExcel.drop()
	#db.cutCorbisId.drop()
	#db.errorCorbisId.drop()
	#db.cutedCorbisId.drop()
########################class method#######################
	def __del__(self):
		self.dele()

	def __init__(self):
		self.conn = pymongo.Connection(self.config.serverUrl)
		self.imageDb = self.conn.imageDb
		self.imageDb.authenticate(self.config.mongoUser,self.config.mongoPassw)
		self.imageMeta = self.imageDb.imageMeta
		self.imageConfig = self.imageDb.imageConfig
		self.imageExcel = self.imageDb.imageExcel
		self.cutCorbisId = self.imageDb.cutCorbisId
		self.errorCorbisId = self.imageDb.errorCorbisId
		self.cutedCorbisId = self.imageDb.cutedCorbisId
		self.cutErrorMsg = self.imageDb.cutErrorMsg
		self.delCorbisId = self.imageDb.delCorbisId
		self.reCutCorbisId = self.imageDb.reCutCorbisId
		self.impErrorMsg = self.imageDb.impErrorMsg

	def dele(self):
		if self.conn:
			self.conn.disconnect()

	def dbInit(self):
		#creat db
		self.imageDb = self.conn.imageDb
		#db add user
		self.imageDb.add_user(self.config.mongoUser,self.config.mongoPassw)
		#create image meta table
		self.imageMeta = self.imageDb.imageMeta
		self.imageConfig = self.imageDb.imageConfig
		self.imageExcel = self.imageDb.imageExcel
		self.cutCorbisId = self.imageDb.cutCorbisId
		self.errorCorbisId = self.imageDb.errorCorbisId
		self.cutedCorbisId = self.imageDb.cutedCorbisId
	###########################################
	def addPid(self, pid):
		tmp = {}
		tmp['type'] = 'pid'
		tmp['pid'] = pid
		p = self.imageConfig.find(tmp)
		if p.count() < 1:
			self.imageConfig.insert(tmp)

	def getAllPid(self):
		tmp = {}
		tmp['type'] = 'pid'
		pCur = self.imageConfig.find(tmp)
		r = []
		for row in pCur:
			r.append(row['pid'])
		return r

	def removePid(self, pid):
		tmp = {}
		tmp['type'] = 'pid'
		tmp['pid'] = pid
		self.imageConfig.remove(tmp)
		tmpCorbis = {}
		tmpCorbis['pid'] = pid
		self.cutCorbisId.remove(tmpCorbis)

	def removeAllPid(self):
		tmp = {}
		tmp['type'] = 'pid'
		self.imageConfig.remove(tmp)
	##########################################
	def addCorbisId(self,pid,corbisId):
		tmp = {}
		tmp['pid'] = pid
		tmp['corbisId'] = corbisId
		self.cutCorbisId.insert(tmp)

	def getCorbisId(self,pid):
		tmp = {}
		tmp['pid'] = pid		
		r = self.cutCorbisId.find_one(tmp)
		if r == None:
			return None
		return r['corbisId']

	def removeCorbisId(self,pid,corbisId):
		tmp = {}
		tmp['pid'] = pid
		tmp['corbisId'] = corbisId
		self.cutCorbisId.remove(tmp)
	##########################################
	def addCutedCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		self.cutedCorbisId.insert(tmp)
	def removeCutedCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		self.cutedCorbisId.remove(tmp)
	##########################################
	def addErrorCorbisId(self,corbisId,errorMsg):
		tmp = {}
		tmp['corbisId'] = corbisId
		tmp['errorMsg'] = errorMsg
		self.errorCorbisId.insert(tmp)
	def getErrorCorbisId(self):
		r = self.errorCorbisId.find_one()
		if r == None:
			return ''
		return r['corbisId']

	def getAllErrorCorbisId(self):
		r = []
		tmp = self.errorCorbisId.find()
		for row in tmp:
			r.append(row['corbisId'])
		return r

	def removeErrorCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		self.errorCorbisId.remove(tmp)
	##########################################
	def insertImageExcel(self,data):
		self.imageExcel.insert(data)

	def getImageExcelByCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		data = self.imageExcel.find_one(tmp)
		if data == None:
			return None
		return data['data']

	def getImageExcelByCorbisIdInfo(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		return self.imageExcel.find_one(tmp)

	def removeImageExcelByCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		return self.imageExcel.remove(tmp)

	##########################################
	def insertImageConfig(self,data):
		self.imageConfig.insert(data)	

	def getImageConfig(self,type):
		tmp = {}
		tmp['type'] = type
		return self.imageConfig.find_one(tmp)
	##########################################
	def insertImageMeta(self,data):
		self.imageMeta.insert(data)

	def getImageMetaByCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		#print tmp
		return self.imageMeta.find_one(tmp)	

	def getImageMetaById(self,iid):
		#print '{\"id\":%s}' % iid
		strTmp = '%s' % iid
		tmp = {}
		tmp['id'] = long(strTmp)
		#print tmp
		return self.imageMeta.find_one(tmp)

	def removeImageMetaByCorbisId(self,corbisId):
		tmp = {}
		tmp['corbisId'] = corbisId
		self.imageMeta.remove(tmp)

	##########################################
	def addCutErrorMsg(self,fileName,corbisId,msg):
		tmp = {}
		tmp['fileName'] = fileName
		tmp['corbisId'] = corbisId
		tmp['errorMsg'] = msg
		self.cutErrorMsg.insert(tmp)
	#########################################
	def addDelCorbisId(self,storageId,corbisId):
		tmp = {}
		tmp['storageId'] = storageId
		tmp['corbisId'] = corbisId
		tmp['status'] = 0
		self.delCorbisId.insert(tmp)

	def modifDelCorbisId(self,storageId,corbisId):
		q = {}
		q['corbisId'] = corbisId
		tmp = self.delCorbisId.find_one(q)
		if tmp == None:
			tmp = {}
			tmp['storageId'] = storageId
			tmp['corbisId'] = corbisId			
			tmp['status'] = 1
			self.delCorbisId.insert(tmp)
		else:
			tmp['status'] = 1
			self.delCorbisId.save(tmp)		

	def getDelCorbisId(self):
		q = {}
		q['status'] = 0
		tmp = self.delCorbisId.find(q).limit(100)		
		if tmp == None:
			return None
		r = []
		for row in tmp:
			sr = []
			sr.append(row['storageId'])
			sr.append(row['corbisId'])
			r.append(sr)
		return r

	#########################################
	def addReCutCorbisId(self,storageId,corbisId):
		tmp = {}
		tmp['storageId'] = storageId
		tmp['corbisId'] = corbisId
		tmp['status'] = 0
		self.reCutCorbisId.insert(tmp)

	def modifReCutCorbisId(self,storageId,corbisId):
		q = {}
		q['corbisId'] = corbisId
		tmp = self.reCutCorbisId.find_one(q)
		if tmp == None:
			tmp = {}
			tmp['storageId'] = storageId
			tmp['corbisId'] = corbisId			
			tmp['status'] = 1
			self.reCutCorbisId.insert(tmp)
		else:
			tmp['status'] = 1
			self.reCutCorbisId.save(tmp)

	def getReCutCorbisId(self):
		q = {}
		q['status'] = 0
		tmp = self.reCutCorbisId.find(q).limit(100)		
		if tmp == None:
			return None
		r = []
		for row in tmp:
			sr = []
			sr.append(row['storageId'])
			sr.append(row['corbisId'])
			if 'fileName' in row.keys():
				sr.append(row['fileName'])
			r.append(sr)
		return r

	#######################################
	def addImpErrorMsg(self,data):
		self.impErrorMsg.insert(data)


