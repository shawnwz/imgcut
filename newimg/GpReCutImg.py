#! /usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb, sys, os, traceback, httplib
import GpLog, GpUtils
from GpConfig import GpConfig
from GpMongoDao import MongoDao
from GpCutImg import CutImg

class ReCutImg:       
    ci = CutImg()
    md = MongoDao()
    config = GpConfig()
    
#####################################################

    def __init__(self):
        pass

    def __del__(self):
        pass

    def rcFormMongo(self):
        while True:
            cids = self.md.getReCutCorbisId()
            if cids == None or len(cids)<1:
                return
            for tmp in cids: 
                if len(tmp) == 3:
                    self.rcImage(tmp[0],tmp[1],tmp[2])
                else:
                    self.rcImage(tmp[0],tmp[1])

    def rcImage(self, storageId, corbisId, fileName=''):
        self.ci.reCutImg(storageId,corbisId,fileName)
        self.md.modifReCutCorbisId(storageId,corbisId)
