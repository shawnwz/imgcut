#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, traceback, httplib
import GpLog, GpUtils
from GpImpExcel import ImpExcel
from GpCutImg import CutImg
from GpMongoDao import MongoDao
from GpConfig import GpConfig

class ImpImg:       
    ie = ImpExcel()
    ci = CutImg()
    md = MongoDao()
#####################################################

    def __init__(self):
        pass

    def __del__(self):
        pass

    def imp(self,xdata,desStorageId,desPath,currPid):
        fileName = xdata['FileName']
        imgFile = xdata['ImageAbsFileName']
        extName = xdata['ImageExtName']
        corbisId = ''
        try:
            #insert into import_images table
            corbisId = self.ie.procRow(xdata)
            GpLog.debug('genCorbisId=%s' % corbisId)                                

            #cut image
            if extName =='gif':
                iptcMsg = self.ci.procGif(desPath,corbisId,imgFile)
            else:
                iptcMsg = self.ci.procImg(desPath,corbisId,imgFile)
            xlsData = {}
            xlsData['corbisId'] = corbisId
            xlsData['id'] = xdata['id']
            xlsData['data'] = xdata
            #corbisId
            iptcMsg['corbisId'] = corbisId
            iptcMsg['storageId'] = desStorageId
            iptcMsg['id'] = xdata['id']
            iptcMsg['originalFilename'] = fileName+'.'+extName
            iptcMsg['extName'] = extName
            self.md.insertImageExcel(xlsData)
            self.md.insertImageMeta(iptcMsg)
            self.md.addCorbisId(currPid,corbisId)
        except Exception, e:
            if 'ExcelFileName' in xdata:
                xlsFile = xdata['ExcelFileName'] 
                GpLog.error(' procCutImgError fileName=%s at excel %s; error msg: %s' 
                        % (fileName,xlsFile,e))
            else:
                GpLog.error(' procCutImgError fileName=%s; error msg: %s' 
                        % (fileName,e))
            self.md.addCutErrorMsg(fileName,corbisId,traceback.format_exc())


