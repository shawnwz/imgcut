#! /usr/bin/python
# -*- coding: utf-8 -*-

######################################
#gaopin utils tool
#coding licl
#20141201 
#beijing
######################################

import sys, hashlib, os, random, time

def md5(corbisId):
        s=hashlib.md5(corbisId).hexdigest()
        subPaths=[s[0:2],s[2:4],s[4:6],s[6:8]]
        return subPaths

def md5Str(corbisId):
        subPaths = md5(corbisId)
        return '/%s/%s/%s/%s' % tuple(subPaths)

def filePath(storageId):
        if storageId =="ssd":
                return "/data/data1/Root448/"
        if storageId == "1":
                return "/home/data2/Root/"
        elif storageId == "2":
                return "/home/data/Rootsplash/"
        elif storageId == "3":
                return "/home/data/Root/"
        elif storageId == "4":
                return "/home/data3/Root/"
        elif storageId == "5":
                return "/home/data3/newdata3/"
        elif storageId == "6":
                return "/home/data1/Root/"
        else:
                #return "/home/data1/Root448/"
                return ''

def findImageFileName(path):
        rootPath = path
        if path == '' or path == './':
                rootPath = os.path.abspath('.')
        filePaths = {}
        for root, dirs, files in os.walk(rootPath):
                for name in files:
                        ns = name.rsplit('.',1)
                        if len(ns) ==2:
                                ex = ns[1].lower()
                                if ex == 'jpg' or ex == 'gif' or ex == 'tif':
                                        tmp = []
                                        tmp.append(os.path.join(root, name))
                                        ##ext fileName
                                        tmp.append(ns[1])
                                        ##orgi fileName
                                        tmp.append(ns[0])
                                        ##fileName lower
                                        filePaths[ns[0].lower()] = tmp
        return filePaths

def getImgFileName(imgPaths,fileName):
        #return image path fileName,extFileName
        #add by licl at 20141215,proc fileName lower
        lowerFileName = fileName.lower()
        if lowerFileName in imgPaths:
                tmp = imgPaths[lowerFileName]
                return (tmp[0],tmp[1])  
        return ('','')

def rmPath(rootPath,subPaths):
        for i in range(0,4):
                path=rootPath
                for j in range(0,4-i):
                        path=path+"/"+subPaths[j]
                l=os.listdir(path)
                if len(l)>0:
                        return
                os.rmdir(path)

def mkPath(rootPath,subPaths):
        for i in range(0,4):
                sp=""
                for j in range(0,i+1):
                        sp=sp+subPaths[j]+"/"
                path=rootPath+"/"+sp
                b=os.path.exists(path)
                if b==False:
                        os.chdir(rootPath)
                        for j in range(0,i):
                                os.chdir(subPaths[j])
                        os.mkdir(subPaths[i])

def rmFile(fileName):
        b=os.path.exists(fileName)
        if b:
                os.remove(fileName)
                #print 'remove file: %s' % fileName
        return b

def genPid():
        ran = str(random.randint(0,10000))
        currPid = str(os.getpid())+'-'+ran+'-'+str(time.time())
        return currPid
