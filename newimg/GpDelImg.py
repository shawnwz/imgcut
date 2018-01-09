#! /usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb, sys, os, traceback, httplib
import GpLog, GpUtils
from GpConfig import GpConfig
from GpMongoDao import MongoDao

class DelImg:       
    pathTemp = {'100M':1,
                '50M':1,
                '32M':1,
                '14M':1,
                '2M':1,
                'HOVER':1,
                'PREVIEW':1,
                'WATERMARK':1,
                '/home/ssd1/Root448/THUMBNAIL/305':2,
                '/home/ssd2/Root448/THUMBNAIL/305':2,
                '/home/ssd1/Root448/THUMBNAIL/240':2,
                '/home/ssd2/Root448/THUMBNAIL/240':2,
                '/home/ssd1/Root448/THUMBNAIL/180':2,
                '/home/ssd2/Root448/THUMBNAIL/180':2
                }

    fileType=[".jpg",".gif",".tif"]
    dFSql = 'delete from fr_image_info where corbis_id=\'%s\''
    dOSql = 'delete from orgi_images where CorbisID=\'%s\''

    md = MongoDao()
    config = GpConfig()
    #mysql conn
    conn = None

    #solr client
    httpClient = None
#####################################################

    def __init__(self):
        self.conn = MySQLdb.connect(host=self.config.host,user=self.config.user,
           passwd=self.config.pw,db=self.config.db,port=self.config.port,charset='utf8')

        self.httpClient = httplib.HTTPConnection(self.config.solrHost,self.config.solrPort,timeout=30)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def rmFormMongo(self):
        while True:
            cids = self.md.getDelCorbisId()
            if cids == None or len(cids)<1:
                return
            for tmp in cids:                
                self.rm(tmp[0],tmp[1])

    def rm(self,storageId,corbisId):
        GpLog.debug('begin rm corbisId=%s' % corbisId)
        #rm image
        self.rmImage(storageId,corbisId)
        #rm mysql 
        self.rmTable(corbisId)
        #rm mongo, don't rm mongo?
        #self.rmMongo(corbisId)
        #rm solr
        self.rmSolr(corbisId)
        ##update mongo
        self.md.modifDelCorbisId(storageId,corbisId)
        GpLog.debug('end rm corbisId=%s' % corbisId)

    def rmImage(self,storageId,corbisId):
        GpLog.debug("begin rmImage : "+corbisId)    
        rootPath=GpUtils.filePath(storageId)
        if rootPath == '':
            GpLog.error('storageId notfound path,storageId=%s' % storageId)
            return
        #subPaths=utils.md5Str(corbisId)
        md5Path = GpUtils.md5Str(corbisId)
        tmpft = ''
        for pt in self.pathTemp.keys():
            path = ''
            if self.pathTemp[pt] == 1:
                path = rootPath + pt + md5Path
                b = os.path.exists(path)
                if not b:
                    GpLog.debug("rmfile not found path : "+path)
                    continue
            else:
                path = pt + md5Path
            fileName = path+'/'+corbisId
            if tmpft == '':
                for ft in self.fileType:
                    b = GpUtils.rmFile(fileName+ft)
                    if b:
                        tmpft = ft
                        break
            else:
                b = GpUtils.rmFile(fileName+tmpft)
                if not b:
                    GpLog.debug("notfound image : %s%s" % (fileName,tmpft))
        GpLog.debug("end rmImage : "+corbisId)

    def rmTable(self,corbisId):
        cur = self.conn.cursor()
        print self.dFSql
        try:
            cur.execute(self.dFSql % corbisId)
            cur.execute(self.dOSql % corbisId)
            self.conn.commit()
        except Exception,ex:
            self.conn.rollback()
            GpLog.error('delete table error corbisId=%s, error=%s' % (corbisId,ex))
            print traceback.format_exc()
            raise
        finally:
            if cur:
                cur.close()

    def rmMongo(self,corbisId):
        self.md.removeImageMetaByCorbisId(corbisId)
        self.md.removeImageExcelByCorbisId(corbisId)

    def rmSolr(self,corbisId):
        self.httpClient.request("GET",self.config.solrPath.format(corbisId))
        response = self.httpClient.getresponse()
        if 200 != response.status:
            GpLog.error(str(response.status)+" rm index corbisId : "+corbisId)
        response.read()

