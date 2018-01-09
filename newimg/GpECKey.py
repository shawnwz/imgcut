#! /usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb, traceback
from GpConfig import GpConfig

class ECKey:
	config = GpConfig()
	######enKey cnKey fr_keyword_collection
	e2c = {}
	c2e = {}

##################################################
	def __init__(self):
		self.loadKey()

	def loadKey(self):
		conn = None
		cur = None
		try:
			conn = MySQLdb.connect(host=self.config.host,user=self.config.user,
				passwd=self.config.pw,db=self.config.db,port=self.config.port,charset='utf8')
			kwSql = 'select english,chinese from fr_keyword_collection'
			cur = conn.cursor()
			cur.execute(kwSql)
			for en, cn in cur.fetchall():
				enlow = en.lower().strip()
				if enlow in self.e2c:
					self.e2c[enlow] += '|' + cn
				else:                        
					self.e2c[enlow] = '|' + cn
				if cn in self.c2e:
					self.c2e[cn] += '|' + en
				else:
					self.c2e[cn] = '|' + en 
		except Exception,ex:
			GpLog.error('load fr_keyword_collection, error=%s' % ex)
			print traceback.format_exc()  
		finally:
			if cur:
				cur.close()
			if conn:
				conn.close()

	def cnMapen(self,cns,sp):
		if len(self.c2e)<100:
			GpLog.error("chinese keyword is null!")
		if cns == None or cns == '':
			return ('','')
		cndes = ''
		endes = ''
		for cn in cns.split(sp):
			cndes += '|'+cn
			if cn in self.c2e:
				endes += self.c2e[cn]
		cndes = cndes[1:]
		endes = endes[1:]
		return (endes,cndes)

	def enMapcn(self,ens,sp):
		if len(self.e2c)<100:
			GpLog.error("english keyword is null!")
		if ens == None or ens == '':
			return ('','')
		cndes = ''
		endes = ''
		for en in ens.split(sp):
			endes += '|'+en
			enlow = en.lower().strip()
			if enlow in self.e2c:
				cndes += self.e2c[enlow]
		cndes = cndes[1:]
		endes = endes[1:]
		return (endes,cndes)









