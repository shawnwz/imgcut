import MySQLdb, sys, traceback, time, datetime, types, os, xlrd

import GpLog, GpUtils
from GpConfig import GpConfig
from email.header import UTF8

class GroupingObject(object):

	iGroupSql  = 'insert into fr_image_group'
	iGroupSql += '(name,category_id,num,photographer,intro,status,create_time,update_time,cover_image,location,back_name,code,url_code) '
	iGroupSql += 'values(%s,null,null,null,null,0,now(),now(),null, null,null,null,null)'

	sGroupIDSql = 'select id from fr_image_group'
	sGroupIDSql += 'where name = %s'

	iGroupImageSql = 'insert into fr_imagegroup_image'
	iGroupImageSql += '(image_group_id,image_id)'
	iGroupImageSql += 'values(%s, %s)'

	def __init__(self, file_name):

		self.file_name = file_name
		if not os.path.exists(file_name):
			raise Exception("File do not exists")
		f = xlrd.open_workbook(file_name)
		# get the first worksheet
		work_sheet = f.sheet_by_index(0)
		# read a row
		self.gname = work_sheet.col_values(0)[1:]
		self.fname = work_sheet.col_values(1)[1:]
		self.intro = work_sheet.col_values(2)[1:]
		self.num = work_sheet.col_values(3)[1:]
		GpLog.debug('Successully get file name and group name') 
		#logging.info('Successully get file name and group name') 
		GpLog.debug('gname is ' + self.gname[2] + ' fname is '+ self.fname[2] + ' intro is ' + self.intro[2])
		#logging.info('gname is ' + gname + ' fname is '+ fname)
		# set up the config
		self.config = GpConfig()
		# set up the db handler
		# default port is already 3306! 
		try:
			#self.db = MySQLdb.connect(host=config.host,user=config.user,passwd=config.pw, db=config.db) 
			self.conn = MySQLdb.connect(host=self.config.host,user=self.config.user,
				passwd=self.config.pw,db=self.config.db,port=self.config.port,charset='utf8')
		except:
			raise Exception("Cannot establish connection to DB!!") 
	def __del__(self):
		self.conn.close()

	def execute(self):
		"""Main logic for execution.
		"""
		GpLog.debug("start execute")
		cur = self.conn.cursor() 
		cur2 = self.conn.cursor()
		for f in self.fname:
			v = cur.execute("SELECT CorbisID FROM import_images WHERE OrgiID = '%s'" % (f))
			if v < 1:
				GpLog.debug("!!!!!!!!!!!!!!!!!!Corbis ID doesn't exist for id %s, please check " % (f))
				pass
			else:
				GpLog.debug("corbis id check pass")
		for f, g, t, m in zip(self.fname, self.gname, self.intro, self.num):
			try:
				GpLog.debug("SELECT CorbisID FROM import_images WHERE OrgiID = '%s'" % (f))
				n = cur.execute("SELECT CorbisID FROM import_images WHERE OrgiID = '%s' ORDER BY Id DESC" % (f))
				# exe successfully = 1  
				#GpLog.debug(n)
				if n>=1:
					cid = cur.fetchone()
					cidu=cid[0]
					if type(cidu) is unicode:
						cidx = cidu.encode('UTF8')
					cidint = int(cidx)
					#GpLog.debug("xxxxx select corbisID = %d" % (cidint))
					#GpLog.debug("SELECT * FROM fr_image_group WHERE name='%s'" % (g))
					gp = cur.execute("SELECT * FROM fr_image_group WHERE name='%s'" % (g))
					#GpLog.debug("gp = %s" % (gp))
					if gp == 0:
						GpLog.debug("xxxxxxxxx")
						cur2.execute("insert into fr_image_group (name,category_id,num,photographer,intro,status,create_time,update_time,cover_image,location,back_name,code,url_code) values('%s',null,'%d',null,'%s',0,now(),now(),null, null,null,null,null)" % (g,int(m),t))
						self.conn.commit()
					#query group id
					#GpLog.debug("group exist, selecting group id ")
					cur.execute("SELECT id FROM fr_image_group WHERE name='%s'" % (g))
					groupid = cur.fetchone()
					gidlong = groupid[0]
					groupidint = int(gidlong)
					#GpLog.debug = ("groupid int = %d " % (groupidint))
					
					isdup = cur.execute("SELECT * FROM fr_imagegroup_image WHERE image_group_id = '%d' AND image_id='%s'" % (groupidint, cidint))
					if isdup == 0:
						GpLog.debug("insert into fr_imagegroup_image (image_group_id, image_id) values('%d','%d')" % (groupidint, cidint))
						cur2.execute("insert into fr_imagegroup_image (image_group_id, image_id) values('%d','%d')" % (groupidint, cidint))
						self.conn.commit()
					else:
						GpLog.debug("image '%d' already in group %d !   please check" % (cidint,groupidint));
				else:
					pass		
			except MySQLdb.Error,e:
				self.conn.rollback()
				try:
					print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
				except IndexError:
					print "MySQL Error: %s" % str(e)		
