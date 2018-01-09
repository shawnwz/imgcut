#! /usr/bin/python
# -*- coding: utf-8 -*-

######################################
#gaopin cut image class
#coding lvf & licl
#20141101 
#beijing
######################################

import sys, os, errno, ConfigParser, math, logging, traceback, shutil
from pgmagick import Image, Geometry, Blob
from images2gif import readGif
from images2gif import writeGif

from PIL import Image as PIL_Image
import GpLog, GpUtils

class CutImg:
#############class propreties#############################	
        #vars:
        fuzzy_ratio = 1
        #w/h ratio, value=1:strict match, value>1:loose match
        density_factor = 300  #default density factor
        inch2cm = 2.54
        #writeExif = 1  #TODO only test
        #paras 11x9
        para_m = 11
        para_n = 9
        paras = [[0 for col in range(para_m)] for row in range(para_n)]	
        #paras -outfileSuffix -w -d -lmp -hmp -q -sharpen -ppi -saveInFolder -grayAdjust -useAsIntermediate
        paras[0] = ['50M', '>4500','<6000','45m', '70m',  95,0,  300,1,1,0]
        paras[1] = ['32M', '>3300','<4500','30m', '44.9m',95,0,  300,1,1,0]
        paras[2] = ['14M', '>2000','<3300','9m',  '29.9m',95,0,  300,1,1,0]
        paras[3] = ['2M',  '<1280','<1280','1.5m','8.9m', 95,0,  72, 1,1,0]
        paras[4] = ['640K','<650', '<650', '',    '',     90,0.3,72, 1,1,0]  # -grayAdjust = 1?
        paras[5] = ['650', '650',  '650',  '',    '',     90,0.3,72, 1,0,0]
        paras[6] = ['305', '305',  '0',    '',    '',     90,0.4,72, 2,0,0]
        paras[7] = ['240', '240',  '0',    '',    '',     90,0.6,72, 2,0,0]
        paras[8] = ['180', '180',  '180',  '',    '',     90,0.6,72, 2,0,0]

        sizeLimits = ['70m', '45m', '30m', '9m', '0', '0', '0', '0', '0']
        moveFolderName = ['100M', '50M', '32M', '14M', '2M', 'HOVER']
        sizeLimitsPathName = ['50M', '32M', '14M', '2M', 'HOVER', 'PREVIEW', 
                        '/home/ssd%s/Root448/THUMBNAIL/305',
                        '/home/ssd%s/Root448/THUMBNAIL/240', 
                        '/home/ssd%s/Root448/THUMBNAIL/180']
        ratio_m = 8
        r = [[0 for col in range(ratio_m)] for row in range(para_n)]

        pano_factor =  [[0.75, 1.333], 
                        [0.75, 1.333], 
                        [0.5624, 1.777], 
                        [2.369, 2.369], 
                        [1, 1], [1, 1], 
                        [1, 1], [1, 1],
                        [1, 1]]  #@_@20141114+

        INT_BIGNUMBER = 65535

#########################class fun###############################	
	def __init__(self):
		for i in range(0, len(self.sizeLimits)):
                        self.sizeLimits[i] = self.str2num_(self.sizeLimits[i])
		#GpLog.debug(self.sizeLimits)
                #update paras[]
                for i in range(self.para_n):
                        mp_  = self.paras[i][0]
                        w_   = self.paras[i][1]
                        h_   = self.paras[i][2]
                        lmp_ = self.paras[i][3]
                        hmp_ = self.paras[i][4]
                        (ri, nmpi, wi, hi, isratioi) = self.getRatio(mp_, w_, h_, lmp_, hmp_)
                        self.r[i] = ri
                        self.paras[i][1] = nmpi
                        self.paras[i][2] = isratioi
                        self.paras[i][3] = wi
                        self.paras[i][4] = hi
                #GpLog.debug(self.paras)
                #GpLog.debug(self.r)

        def reCutImg(self,storageId,corbisId,fileName=''):
                storageId = str(storageId)
                corbisId = corbisId                
                if fileName == None:
                        fileName = ''
                md5Path = GpUtils.md5Str(corbisId)                
                rootPath=GpUtils.filePath(storageId)                
                if rootPath == '':
                        GpLog.error("notfound root path, storageId=%s" % storageId)
                        return
                maxPath = ''
                exFileName = '.jpg'
                if fileName == '':
                        for sizePath in self.moveFolderName:
                                path = rootPath + sizePath + md5Path
                                b = os.path.exists(path)
                                if b:
                                        tmppath = path + '/'+corbisId+'.jpg'
                                        b = os.path.exists(tmppath)
                                        if b:
                                                maxPath = tmppath
                                                break
                                        tmppath = path + '/'+corbisId+'.gif'
                                        b = os.path.exists(tmppath)
                                        if b:
                                                maxPath = tmppath
                                                exFileName = '.gif'
                                                break
                                        tmppath = path + '/'+corbisId+'.tif'
                                        b = os.path.exists(tmppath)
                                        if b:
                                                maxPath = tmppath
                                                exFileName = '.tif'
                                                break
                else:
                        maxPath = fileName
                        b = os.path.exists(maxPath)
                        if not b:
                                GpLog.error("notfound image file:%s" % orgiFileName)
                                return

                if maxPath == '':
                        GpLog.error("notfound max image, storageId=%s,corbisId=%s" % (storageId,corbisId))
                        return
                
                desPath = rootPath
                inputImg = Image(maxPath)
                int_width = inputImg.columns()
                int_height = inputImg.rows()

                colorSpace = inputImg.attribute("JPEG-Colorspace-Name")
                #number of channels
                nChannel = 3
                if colorSpace == 'GRAYSCALE':
                        nChannel = 1
                elif colorSpace == 'CMYK':
                        nChannel = 4

                imgMaxSize = int_width * int_height * nChannel
                ratio = float(int_width) / float(int_height)

                if not fileName == '':
                        for i in range(0, len(self.sizeLimits)):
                                if imgMaxSize > self.sizeLimits[i]:
                                        movePath = desPath + self.moveFolderName[i] + md5Path
                                        moveFileName = corbisId + exFileName
                                        self.mkdir_p(movePath)
                                        tmpStr = movePath + '/' + moveFileName;
                                        self.copy_p(fileName, tmpStr)                                        
                                        break

                for j in range(0, self.para_n):
                        if (int_width * int_height * nChannel) <= self.sizeLimits[j]:
                                GpLog.debug('width: %d, height: %d. size: %.1fM, image larger than %s will be resize only, skip this one.' % 
                                        (int_width, int_height, imgMaxSize/1024/1024, self.sizeLimitsPathName[j]))
                                continue
                        #-outFileSuffix         -nmp    -isratio -w     -h   -q -sharpen -ppi -saveInFolder -grayAdjust -useIntermediateAsInput
                        #paras[0] = ['50m', 50*1024*1024, 1,     4500, 6000, 95,  0,      300,  1,            1,          0]
                        p_ofs = self.paras[j][0]
                        p_nmp = self.paras[j][1]
                        p_isr = self.paras[j][2]
                        p_w   = self.paras[j][3]
                        p_h   = self.paras[j][4]
                        p_q   = self.paras[j][5]
                        p_s   = self.paras[j][6]
                        p_ppi = self.paras[j][7]
                        p_sif = self.paras[j][8]
                        p_ga  = self.paras[j][9]
                        p_uiai= self.paras[j][10]
                        if p_ga:
                                p_nmp = p_nmp / nChannel

                        if max(int_height, int_width) > 2 * min(int_height, int_width):  #@_@20141105+- #@_@20141112+-
                                #GpLog.debug('pano:')
                                w_factor = self.pano_factor[j][0]
                                h_factor = self.pano_factor[j][1]
                                (resize_width, resize_height) = self.calcWH_patched(ratio, p_nmp, p_w, p_h, self.r[j], p_isr, w_factor, h_factor)
                        else:
                                (resize_width, resize_height) = self.calcWH(ratio, p_nmp, p_w, p_h, self.r[j], p_isr)
                        resize_width = int(resize_width)
                        resize_height = int(resize_height)
                        #GpLog.debug('calcWH: %d * %d' % (resize_width, resize_height))
                        if resize_width < 0 or resize_height < 0:
                                GpLog.error('Size error while attempting to resize to %s.\nWidth: %d\nHeight: %d\nLimits: W=%d, H=%d\n' % (
                                                p_ofs, int_width, int_height, p_w, p_h))
                                continue
                        resizeImg = Image(inputImg)
                        #resize
                        if resize_width == 0:  #@_@20141112+-
                                resize_width = self.INT_BIGNUMBER
                        if resize_height == 0:
                                resize_height = self.INT_BIGNUMBER
                        geo_resize = Geometry(resize_width, resize_height)
                        resizeImg.scale(geo_resize)
                        #GpLog.debug('Resized to: %d * %d ' % ( resize_width, resize_height ))

                        #sharpen
                        sharpen_factor = p_s
                        if sharpen_factor > 0: resizeImg.sharpen(sharpen_factor)
                        #GpLog.debug('Sharpened: %.1f' % ( sharpen_factor ))

                        #quality
                        quality_factor = p_q
                        resizeImg.quality(quality_factor)
                        #GpLog.debug('Quality set to: %d' % ( quality_factor ))

                        #density
                        density_factor = p_ppi
                        geo_density = Geometry(density_factor, density_factor)
                        resizeImg.density(geo_density)
                        #GpLog.debug('Density set to: %d x %d' % ( density_factor, density_factor ))

                        #mkdir or rename output_file_name
                        outPutFileName = ''
                        if p_sif == 1:                                
                                output_path = desPath + self.sizeLimitsPathName[j] + md5Path
                                output_file_absName = corbisId + '.jpg'                                
                                self.writeImg(output_path, output_file_absName, resizeImg)
                                outPutFileName = output_path+'/'+output_file_absName
                        ####write image to ssd
                        elif p_sif == 2:
                                output_path = (self.sizeLimitsPathName[j] % '1') + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)
                                #########
                                outPutFileName = output_path+'/'+output_file_absName

                                output_path = (self.sizeLimitsPathName[j] % '2') + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)
                        else:                                
                                output_path = self.sizeLimitsPathName[j] + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)                        
                                outPutFileName = output_path+'/'+output_file_absName
                        
                        #if use intermediate as input
                        if p_uiai:
                                inputImg = resizeImg

        def procImg(self, desPath, corbisId, fileName):                
                md5Path = GpUtils.md5Str(corbisId)
                inputImg = None
                GpLog.debug('imgFileName is %s' % fileName)
                if os.path.exists(fileName):
                        inputImg = Image(fileName)
                else:
                        raise Exception('image [%s] not found!' % fileName)
                #process iptc info
                iptcMsg = self.iptc(inputImg)		

                #orgi image fileName
                iptcMsg['filePathName'] = fileName
                iptcMsg['fileSize'] = os.path.getsize(fileName)

                int_width = inputImg.columns()
                int_height = inputImg.rows()
                ratio = float(int_width) / float(int_height)
                iptcMsg['ratio'] = int(ratio*100)/100.0

                #remove EXIF
                blob = Blob()
                inputImg.profile("*", blob)
                #GpLog.debug('Deleted EXIF IPTC ICC.')                

                #copy original image file to max size
                nChannel = iptcMsg['channel']
                imgMaxSize = int_width * int_height * nChannel
                iptcMsg['maxSize'] = imgMaxSize
                for i in range(0, len(self.sizeLimits)):
                        if imgMaxSize > self.sizeLimits[i]:
                                movePath = desPath + self.moveFolderName[i] + md5Path
                                moveFileName = corbisId + '.jpg'
                                self.mkdir_p(movePath)
                                tmpStr = movePath + '/' + moveFileName;
                                self.copy_p(fileName, tmpStr) 
                                iptcMsg['maxSizeName'] =   self.moveFolderName[i]
                                iptcMsg['maxSizeFileName'] =  tmpStr

                                #add by licl at 20150107,save max image info
                                #modify by licl at 20150110
                                #subImgInfo = {}
                                #subImgInfo['width'] = int_width
                                #subImgInfo['height'] = int_height
                                #subImgInfo['imageSize'] = imgMaxSize
                                #subImgInfo['filePath'] = tmpStr
                                #subImgInfo['fileSize'] = os.path.getsize(tmpStr)
                                #iptcMsg["_"+self.moveFolderName[i]] = subImgInfo
                                break

                ##cut img
                for j in range(0, self.para_n):
                        if (int_width * int_height * nChannel) <= self.sizeLimits[j]:
                                GpLog.debug('width: %d, height: %d. size: %.1fM, image larger than %s will be resize only, skip this one.' % 
                                        (int_width, int_height, imgMaxSize/1024/1024, self.sizeLimitsPathName[j]))
                                continue
                        #-outFileSuffix         -nmp    -isratio -w     -h   -q -sharpen -ppi -saveInFolder -grayAdjust -useIntermediateAsInput
                        #paras[0] = ['50m', 50*1024*1024, 1,     4500, 6000, 95,  0,      300,  1,            1,          0]
                        p_ofs = self.paras[j][0]
                        p_nmp = self.paras[j][1]
                        p_isr = self.paras[j][2]
                        p_w   = self.paras[j][3]
                        p_h   = self.paras[j][4]
                        p_q   = self.paras[j][5]
                        p_s   = self.paras[j][6]
                        p_ppi = self.paras[j][7]
                        p_sif = self.paras[j][8]
                        p_ga  = self.paras[j][9]
                        p_uiai= self.paras[j][10]
                        if p_ga:
                                p_nmp = p_nmp / nChannel

                        if max(int_height, int_width) > 2 * min(int_height, int_width):  #@_@20141105+- #@_@20141112+-
                                #GpLog.debug('pano:')
                                w_factor = self.pano_factor[j][0]
                                h_factor = self.pano_factor[j][1]
                                (resize_width, resize_height) = self.calcWH_patched(ratio, p_nmp, p_w, p_h, self.r[j], p_isr, w_factor, h_factor)
                        else:
                                (resize_width, resize_height) = self.calcWH(ratio, p_nmp, p_w, p_h, self.r[j], p_isr)
                        resize_width = int(resize_width)
                        resize_height = int(resize_height)
                        #GpLog.debug('calcWH: %d * %d' % (resize_width, resize_height))
                        if resize_width < 0 or resize_height < 0:
                                GpLog.error('Size error while attempting to resize to %s.\nWidth: %d\nHeight: %d\nLimits: W=%d, H=%d\n' % (
                                                p_ofs, int_width, int_height, p_w, p_h))
                                continue
                        resizeImg = Image(inputImg)
                        #resize
                        if resize_width == 0:  #@_@20141112+-
                                resize_width = self.INT_BIGNUMBER
                        if resize_height == 0:
                                resize_height = self.INT_BIGNUMBER
                        geo_resize = Geometry(resize_width, resize_height)
                        resizeImg.scale(geo_resize)
                        #GpLog.debug('Resized to: %d * %d ' % ( resize_width, resize_height ))

                        #sharpen
                        sharpen_factor = p_s
                        if sharpen_factor > 0: resizeImg.sharpen(sharpen_factor)
                        #GpLog.debug('Sharpened: %.1f' % ( sharpen_factor ))

                        #quality
                        quality_factor = p_q
                        resizeImg.quality(quality_factor)
                        #GpLog.debug('Quality set to: %d' % ( quality_factor ))

                        #density
                        density_factor = p_ppi
                        geo_density = Geometry(density_factor, density_factor)
                        resizeImg.density(geo_density)
                        #GpLog.debug('Density set to: %d x %d' % ( density_factor, density_factor ))

                        #mkdir or rename output_file_name
                        outPutFileName = ''
                        if p_sif == 1:                                
                                output_path = desPath + self.sizeLimitsPathName[j] + md5Path
                                output_file_absName = corbisId + '.jpg'                                
                                self.writeImg(output_path, output_file_absName, resizeImg)
                                outPutFileName = output_path+'/'+output_file_absName
                        ####write image to ssd
                        elif p_sif == 2:
                                output_path = (self.sizeLimitsPathName[j] % '1') + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)
                                #########
                                outPutFileName = output_path+'/'+output_file_absName

                                output_path = (self.sizeLimitsPathName[j] % '2') + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)
                        else:                                
                                output_path = self.sizeLimitsPathName[j] + md5Path
                                output_file_absName = corbisId + '.jpg'
                                self.writeImg(output_path, output_file_absName, resizeImg)                        
                                outPutFileName = output_path+'/'+output_file_absName
                        #image info 
                        subImgInfo = {}
                        #subImgInfo['type'] = p_ofs
                        #subImgInfo['corbisId'] = corbisId
                        subImgInfo['width'] = resize_width
                        subImgInfo['height'] = resize_height
                        #calc imageSize                        
                        subImgInfo['imageSize'] = resizeImg.columns()*resizeImg.rows()*nChannel                        
                        subImgInfo['filePath'] = outPutFileName
                        subImgInfo['fileSize'] = os.path.getsize(outPutFileName)
                        
                        #iptcMsg["_"+p_ofs] = subImgInfo
                        iptcMsg[p_ofs] = subImgInfo

                        #if use intermediate as input
                        if p_uiai:
                                inputImg = resizeImg
                ####return iptc
                return iptcMsg

        def procGif(self, desPath, corbisId, fileName):   
                GpLog.debug('Entering proGif.....')             
                md5Path = GpUtils.md5Str(corbisId)
                inputImg = None
                GpLog.debug('imgFileName is %s' % fileName)
                if os.path.exists(fileName):
                        inputImg = Image(fileName)
                else:
                        raise Exception('image [%s] not found!' % fileName)
                #process iptc info
                iptcMsg = self.iptc(inputImg)        

                #orgi image fileName
                iptcMsg['filePathName'] = fileName
                iptcMsg['fileSize'] = os.path.getsize(fileName)

                int_width = inputImg.columns()
                int_height = inputImg.rows()
                ratio = float(int_width) / float(int_height)
                iptcMsg['ratio'] = int(ratio*100)/100.0

                #remove EXIF
                blob = Blob()
                inputImg.profile("*", blob)
                #GpLog.debug('Deleted EXIF IPTC ICC.')                

                #copy original image file to max size
                nChannel = iptcMsg['channel']
                imgMaxSize = int_width * int_height * nChannel
                iptcMsg['maxSize'] = imgMaxSize
                for i in range(0, len(self.sizeLimits)):
                        if imgMaxSize > self.sizeLimits[i]:
                                movePath = desPath + self.moveFolderName[i] + md5Path
                                moveFileName_gif = corbisId + '.gif'
                                moveFileName_jpg = corbisId + '.jpg'
                                self.mkdir_p(movePath)
                                tmpStr_gif = movePath + '/' + moveFileName_gif;
                                tmpStr_jpg = movePath + '/' + moveFileName_jpg;
                                self.copy_p(fileName, tmpStr_gif) 
                                self.copy_p(fileName, tmpStr_jpg) 
                                iptcMsg['maxSizeName'] =   self.moveFolderName[i]
                                iptcMsg['maxSizeFileName'] =  tmpStr_jpg

                                #add by licl at 20150107,save max image info
                                #modify by licl at 20150110
                                #subImgInfo = {}
                                #subImgInfo['width'] = int_width
                                #subImgInfo['height'] = int_height
                                #subImgInfo['imageSize'] = imgMaxSize
                                #subImgInfo['filePath'] = tmpStr
                                #subImgInfo['fileSize'] = os.path.getsize(tmpStr)
                                #iptcMsg["_"+self.moveFolderName[i]] = subImgInfo
                                break

                ##cut img
                for j in range(0, self.para_n):
                        if (int_width * int_height * nChannel) <= self.sizeLimits[j]:
                                GpLog.debug('width: %d, height: %d. size: %.1fM, image larger than %s will be resize only, skip this one.' % 
                                        (int_width, int_height, imgMaxSize/1024/1024, self.sizeLimitsPathName[j]))
                                continue
                        #-outFileSuffix         -nmp    -isratio -w     -h   -q -sharpen -ppi -saveInFolder -grayAdjust -useIntermediateAsInput
                        #paras[0] = ['50m', 50*1024*1024, 1,     4500, 6000, 95,  0,      300,  1,            1,          0]
                        p_ofs = self.paras[j][0]
                        p_nmp = self.paras[j][1]
                        p_isr = self.paras[j][2]
                        p_w   = self.paras[j][3]
                        p_h   = self.paras[j][4]
                        p_q   = self.paras[j][5]
                        p_s   = self.paras[j][6]
                        p_ppi = self.paras[j][7]
                        p_sif = self.paras[j][8]
                        p_ga  = self.paras[j][9]
                        p_uiai= self.paras[j][10]
                        if p_ga:
                                p_nmp = p_nmp / nChannel

                        if max(int_height, int_width) > 2 * min(int_height, int_width):  #@_@20141105+- #@_@20141112+-
                                #GpLog.debug('pano:')
                                w_factor = self.pano_factor[j][0]
                                h_factor = self.pano_factor[j][1]
                                (resize_width, resize_height) = self.calcWH_patched(ratio, p_nmp, p_w, p_h, self.r[j], p_isr, w_factor, h_factor)
                        else:
                                (resize_width, resize_height) = self.calcWH(ratio, p_nmp, p_w, p_h, self.r[j], p_isr)
                        resize_width = int(resize_width)
                        resize_height = int(resize_height)
                        #GpLog.debug('calcWH: %d * %d' % (resize_width, resize_height))
                        if resize_width < 0 or resize_height < 0:
                                GpLog.error('Size error while attempting to resize to %s.\nWidth: %d\nHeight: %d\nLimits: W=%d, H=%d\n' % (
                                                p_ofs, int_width, int_height, p_w, p_h))
                                continue
                        
                        if resize_width == 0:  #@_@20141112+-
                                resize_width = self.INT_BIGNUMBER
                        if resize_height == 0:
                                resize_height = self.INT_BIGNUMBER
                        geo_resize = Geometry(resize_width, resize_height)
                        
                        frames = readGif(fileName, False)
                        GpLog.debug('resizing frame.....')
                        for frame in frames:
                            #resizeFrame = Image(frame)
                            #resizeFrame.scale(geo_resize)
                            
                            
                            #frame.scale(geo_resize)
                            
                            #frame.thumbnail((640, 360), PIL_Image.ANTIALIAS )
                            frame.thumbnail((resize_width, resize_height), PIL_Image.NEAREST  )
                            
                            
                            #sharpen
                            sharpen_factor = p_s
                           ## if sharpen_factor > 0: frame.sharpen(sharpen_factor)
                            #GpLog.debug('Sharpened: %.1f' % ( sharpen_factor ))
    
                            #quality
                            quality_factor = p_q
                           ## frame.quality(quality_factor)
                            #GpLog.debug('Quality set to: %d' % ( quality_factor ))
    
                            #density
                            density_factor = p_ppi
                            geo_density = Geometry(density_factor, density_factor)
                           ## frame.density(geo_density)
                            
                       
                        
                        

                        #GpLog.debug('Resized to: %d * %d ' % ( resize_width, resize_height ))



                        #mkdir or rename output_file_name
                        outPutFileName = ''
                        if p_sif == 1:    
                                GpLog.debug('going to write GIF.....')                             
                                output_path = desPath + self.sizeLimitsPathName[j] + md5Path
                                output_file_absName_gif = corbisId + '.gif'  
                                output_file_absName_jpg = corbisId + '.jpg' 
                                self.mkdir_p(output_path)
                                absName_gif = output_path + '/' + output_file_absName_gif      
                                absName_jpg = output_path + '/' + output_file_absName_jpg   
                                writeGif(absName_gif, frames, 0.1, True, False, 0, True, None)  
                                writeGif(absName_jpg, frames, 0.1, True, False, 0, True, None)  
                                GpLog.debug('writed image : ' + absName_gif + ' AND ' + absName_jpg)                   
                                #self.writeImg(output_path, output_file_absName, resizeImg)
                                outPutFileName = output_path+'/'+output_file_absName_jpg
                        ####write image to ssd
                        elif p_sif == 2:
                                GpLog.debug('gong to write GIF.....')
                                output_path = (self.sizeLimitsPathName[j] % '1') + md5Path
                                output_file_absName_gif = corbisId + '.gif'  
                                output_file_absName_jpg = corbisId + '.jpg' 
                                self.mkdir_p(output_path)
                                absName_gif = output_path + '/' + output_file_absName_gif      
                                absName_jpg = output_path + '/' + output_file_absName_jpg   
                                writeGif(absName_gif, frames, 0.1, True, False, 0, True, None)  
                                writeGif(absName_jpg, frames, 0.1, True, False, 0, True, None)  
                                GpLog.debug('writed image : ' + absName_gif + ' AND ' + absName_jpg)  
                                #self.writeImg(output_path, output_file_absName, resizeImg)
                                #########
                                outPutFileName = output_path+'/'+output_file_absName_jpg

                                output_path = (self.sizeLimitsPathName[j] % '2') + md5Path
                                output_file_absName_gif = corbisId + '.gif'  
                                output_file_absName_jpg = corbisId + '.jpg' 
                                self.mkdir_p(output_path)
                                absName_gif = output_path + '/' + output_file_absName_gif      
                                absName_jpg = output_path + '/' + output_file_absName_jpg   
                                writeGif(absName_gif, frames, 0.1, True, False, 0, True, None)  
                                writeGif(absName_jpg, frames, 0.1, True, False, 0, True, None)  
                                GpLog.debug('writed image : ' + absName_gif + ' AND ' + absName_jpg)  
                                #self.writeImg(output_path, output_file_absName, resizeImg)
                        else:   
                                GpLog.debug('gong to write GIF.....')                             
                                output_path = self.sizeLimitsPathName[j] + md5Path
                                output_file_absName_gif = corbisId + '.gif'  
                                output_file_absName_jpg = corbisId + '.jpg' 
                                self.mkdir_p(output_path)
                                absName_gif = output_path + '/' + output_file_absName_gif      
                                absName_jpg = output_path + '/' + output_file_absName_jpg   
                                writeGif(absName_gif, frames, 0.1, True, False, 0, True, None)  
                                writeGif(absName_jpg, frames, 0.1, True, False, 0, True, None)  
                                GpLog.debug('writed image : ' + absName_gif + ' AND ' + absName_jpg)  
                                #self.writeImg(output_path, output_file_absName, resizeImg)                        
                                outPutFileName = output_path+'/'+output_file_absName_jpg
                        #image info 
                        subImgInfo = {}
                        #subImgInfo['type'] = p_ofs
                        #subImgInfo['corbisId'] = corbisId
                        subImgInfo['width'] = resize_width
                        subImgInfo['height'] = resize_height
                        #calc imageSize                        
                        #subImgInfo['imageSize'] = resizeImg.columns()*resizeImg.rows()*nChannel                        
                        subImgInfo['filePath'] = outPutFileName
                        subImgInfo['fileSize'] = os.path.getsize(outPutFileName)
                        
                        #iptcMsg["_"+p_ofs] = subImgInfo
                        iptcMsg[p_ofs] = subImgInfo

                        #if use intermediate as input
                        #if p_uiai:
                        #       inputImg = resizeImg
                ####return iptc
                return iptcMsg


        def iptc(self,inputImg):
                result = {}
                int_width = inputImg.columns()
                int_height = inputImg.rows()
                result['width'] = int_width
                result['height'] = int_height

                if self.fuzzy_ratio < 1:  # e
                        self.fuzzy_ratio = 1
                if int_width > (self.fuzzy_ratio * int_height):  # HORIZONTAL
                        int_ratio_type = 1
                elif int_height > (self.fuzzy_ratio * int_width):  # VERTICAL
                        int_ratio_type = 2
                else:  # SQUARE
                        int_ratio_type = 0
                result['ratioType'] = int_ratio_type

                #read EXIF                
                result['exifMake']         =inputImg.attribute("EXIF:Make")
                result['exifModel']        =inputImg.attribute("EXIF:Model")
                result['exifFocalLength']  =inputImg.attribute("EXIF:FocalLength")
                result['exifExposureTime'] =inputImg.attribute("EXIF:ExposureTime")
                result['exifFNumber']      =inputImg.attribute("EXIF:FNumber")
                result['exifFormat']       =inputImg.format()

                #Resolution
                result['resolution'] = '%d x %d' % ( int_width, int_height )
                
                #calc Print Size
                img_density = inputImg.density()  #@_@20141105+-
                if img_density and (img_density.width() == img_density.height()):
                        int_density = img_density.width()
                else:
                        str_density = inputImg.attribute("EXIF:XResolution")                        
                        if str_density:
                                str_density_lst = str_density.split('/')                                
                                if len(str_density_lst) > 1 and str_density_lst[0] and str_density_lst[1]:
                                        int_density = int(str_density_lst[0]) / int(str_density_lst[1])
                                else:
                                        int_density = density_factor
                        else:
                                int_density = density_factor
                result['imgDensity'] = int_density                
                #if convert to cm
                str_print_size = ''
                if self.inch2cm > 0:
                        str_print_size = str(int_width / int_density * self.inch2cm) + ' x ' + str(
                                int_height / int_density * self.inch2cm) + ' cm'
                else:
                        str_print_size = str(int_width / int_density) + ' x ' + str(int_height / int_density) + ' inches'
                result['printSize'] = str_print_size
                colorSpace = inputImg.attribute("JPEG-Colorspace-Name")                

                #number of channels
                channel = 3
                if colorSpace == 'GRAYSCALE':
                        channel = 1
                elif colorSpace == 'CMYK':
                        channel = 4
                result['colorSpace'] = colorSpace
                result['channel'] = channel
                return result

	#get min & max ratio
	def getRatio(self,mp, w, h, lmp, hmp):
		r = [0.0 for k in range(0, 8)]
		wgminr = 0;
                wrminr = 1;
                hgminr = 2;
                hrminr = 3;
                wgmaxr = 4;
                wrmaxr = 5;
                hgmaxr = 6;
                hrmaxr = 7;

                nmp = self.str2num_(mp)
                lmp = self.str2num_(lmp)
                hmp = self.str2num_(hmp)

                if w[0] == '>' and lmp and hmp:
                        nw = float(w[1:])
                        isratio = 1
                        r[wgminr] = nw * nw * 3 / hmp
                        r[wrminr] = nw * nw * 3 / nmp
                elif w[0] == '<' and lmp and hmp:
                        nw = float(w[1:])
                        isratio = 1
                        r[wgmaxr] = nw * nw * 3 / lmp
                        r[wrmaxr] = nw * nw * 3 / nmp
                else:
                        isratio = 0  # problem here
                        if w[0] == '<':
                                w = w[1:]
                        nw = float(w)
                #h
                if h[0] == '<' and lmp and hmp:
                        nh = float(h[1:])
                        isratio = 1
                        r[hgminr] = lmp / (nh * nh * 3)
                        r[hrminr] = nmp / (nh * nh * 3)
                elif h[0] == '>' and lmp and hmp:
                        nh = float(h[1:])
                        isratio = 1
                        r[hgmaxr] = hmp / (nh * nh * 3)
                        r[hrmaxr] = nmp / (nh * nh * 3)
                else:
                        isratio = 0  # problem here
                        if h[0] == '<':
                                h = h[1:]
                        nh = float(h)
                return (r, nmp, nw, nh, isratio)

        #calculate width and height of resized image
        def calcWH(self, ratio, nmp, nw, nh, r, isratio):
                wgminr = 0;
                wrminr = 1;
                hgminr = 2;
                hrminr = 3;
                wgmaxr = 4;
                wrmaxr = 5;
                hgmaxr = 6;
                hrmaxr = 7;
               
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgmaxr] or r[hrmaxr] or r[wgminr] or r[wrminr] or r[hgminr] or r[hrminr] ):  #0
                        return (nw, nh)
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgmaxr] or r[hrmaxr] ):  #1
                        if ratio < min(r[wgminr], r[hgminr]):
                                #GpLog.debug(' ratio(%.2f) < min(r[wgminr](%.2f),r[hgminr](%.2f)) ' % (ratio, r[wgminr], r[hgminr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio < min(r[wrminr], r[hrminr]):
                                #GpLog.debug(' ratio(%.2f) < min(r[wrminr](%.2f),r[hrminr](%.2f)) ' % (ratio, r[wrminr], r[hrminr]))
                                #GpLog.debug(r)
                                if r[wrminr] < r[hrminr]:
                                        rw = nw
                                        rh = rw / ratio
                                else:
                                        rh = nh
                                        rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                #GpLog.debug("nmp %.1f /rw %.1f ratio %.1f" % (nmp, rw, ratio))
                                rh = nmp / rw
                if not ( r[wgminr] or r[wrminr] or r[hgminr] or r[hrminr] ):  #2
                        if ratio > max(r[wgmaxr], r[hgmaxr]):
                                #GpLog.debug(' ratio(%.2f) > max(r[wgmaxr](%.2f),r[hgmaxr](%.2f)) ' % (ratio, r[wgmaxr], r[hgmaxr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio > max(r[wrmaxr], r[hrmaxr]):
                                #GpLog.debug(' ratio(%.2f) > max(r[wrmaxr](%.2f),r[hrmaxr](%.2f)) ' % (ratio, r[wrmaxr], r[hrmaxr]))
                                #GpLog.debug(r)
                                if r[wrmaxr] > r[hrmaxr]:
                                        rw = nw
                                        rh = rw / ratio
                                else:
                                        rh = nh
                                        rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                if not ( r[wgminr] or r[wrminr] or r[hgmaxr] or r[hrmaxr] ):  #3
                        if ratio > r[wgmaxr] or ratio < r[hgminr]:
                                #GpLog.debug(' ratio(%.2f) > r[wgmaxr](%.2f) or ratio(%.2f) < r[hgminr](%.2f) ' % (
                                #        ratio, r[wgmaxr], ratio, r[hgminr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio > r[wrmaxr]:
                                #GpLog.debug(' ratio(%.2f) > r[wrmaxr](%.2f) ' % (ratio, r[wgmaxr]))
                                #GpLog.debug(r)
                                rw = nw
                                rh = rw / ratio
                        elif ratio < r[hrminr]:
                                #GpLog.debug(' ratio(%.2f) < r[hrminr](%.2f) ' % (ratio, r[hrminr]))
                                #GpLog.debug(r)
                                rh = nh
                                rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgminr] or r[hrminr] ):  #4
                        if ratio < r[wgminr] or ratio > r[hgmaxr]:
                                #GpLog.debug(' ratio(%.2f) < r[wgminr](%.2f) or ratio(%.2f) > r[hgmaxr](%.2f) ' % (
                                #        ratio, r[wgminr], ratio, r[hgmaxr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio < r[wrminr]:
                                #GpLog.debug(' ratio(%.2f) > r[wrmaxr](%.2f) ' % (ratio, r[wgmaxr]))
                                #GpLog.debug(r)
                                rw = nw
                                rh = rw / ratio
                        elif ratio > r[hrmaxr]:
                                #GpLog.debug(' ratio(%.2f) < r[hrminr](%.2f) ' % (ratio, r[hrminr]))
                                #GpLog.debug(r)
                                rh = nh
                                rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                return (rw, rh)

        #calculate width and height of resized image
        def calcWH_patched(self,ratio, nmp, nw, nh, r, isratio, w_factor, h_factor):  #@_@20141105
                wgminr = 0;
                wrminr = 1;
                hgminr = 2;
                hrminr = 3;
                wgmaxr = 4;
                wrmaxr = 5;
                hgmaxr = 6;
                hrmaxr = 7;               
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgmaxr] or r[hrmaxr] or r[wgminr] or r[wrminr] or r[hgminr] or r[hrminr] ):  #0
                        return (nw, nh)
                r[wgmaxr] = r[wgmaxr] * w_factor * w_factor
                r[wrmaxr] = r[wrmaxr] * w_factor * w_factor
                r[wgminr] = r[wgminr] * w_factor * w_factor
                r[wrminr] = r[wrminr] * w_factor * w_factor
                r[hgmaxr] = r[hgmaxr] / h_factor / h_factor
                r[hrmaxr] = r[hrmaxr] / h_factor / h_factor
                r[hgminr] = r[hgminr] / h_factor / h_factor
                r[hrminr] = r[hrminr] / h_factor / h_factor
                nw = nw * w_factor
                nh = nh * h_factor
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgmaxr] or r[hrmaxr] ):  #1
                        if ratio < min(r[wgminr], r[hgminr]):
                                #GpLog.debug(' ratio(%.2f) < min(r[wgminr](%.2f),r[hgminr](%.2f)) ' % (ratio, r[wgminr], r[hgminr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio < min(r[wrminr], r[hrminr]):
                                #GpLog.debug(' ratio(%.2f) < min(r[wrminr](%.2f),r[hrminr](%.2f)) ' % (ratio, r[wrminr], r[hrminr]))
                                #GpLog.debug(r)
                                if r[wrminr] < r[hrminr]:
                                        rw = nw
                                        rh = rw / ratio
                                else:
                                        rh = nh
                                        rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                if not ( r[wgminr] or r[wrminr] or r[hgminr] or r[hrminr] ):  #2
                        if ratio > max(r[wgmaxr], r[hgmaxr]):
                                #GpLog.debug(' ratio(%.2f) > max(r[wgmaxr](%.2f),r[hgmaxr](%.2f)) ' % (ratio, r[wgmaxr], r[hgmaxr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio > max(r[wrmaxr], r[hrmaxr]):
                                #GpLog.debug(' ratio(%.2f) > max(r[wrmaxr](%.2f),r[hrmaxr](%.2f)) ' % (ratio, r[wrmaxr], r[hrmaxr]))
                                #GpLog.debug(r)
                                if r[wrmaxr] > r[hrmaxr]:
                                        rw = nw
                                        rh = rw / ratio
                                else:
                                        rh = nh
                                        rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                if not ( r[wgminr] or r[wrminr] or r[hgmaxr] or r[hrmaxr] ):  #3
                        if ratio > r[wgmaxr] or ratio < r[hgminr]:
                                #GpLog.debug(' ratio(%.2f) > r[wgmaxr](%.2f) or ratio(%.2f) < r[hgminr](%.2f) ' % (
                                #        ratio, r[wgmaxr], ratio, r[hgminr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio > r[wrmaxr]:
                                #GpLog.debug(' ratio(%.2f) > r[wrmaxr](%.2f) ' % (ratio, r[wgmaxr]))
                                #GpLog.debug(r)
                                rw = nw
                                rh = rw / ratio
                        elif ratio < r[hrminr]:
                                #GpLog.debug(' ratio(%.2f) < r[hrminr](%.2f) ' % (ratio, r[hrminr]))
                                #GpLog.debug(r)
                                rh = nh
                                rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                if not ( r[wgmaxr] or r[wrmaxr] or r[hgminr] or r[hrminr] ):  #4
                        if ratio < r[wgminr] or ratio > r[hgmaxr]:
                                #GpLog.debug(' ratio(%.2f) < r[wgminr](%.2f) or ratio(%.2f) > r[hgmaxr](%.2f) ' % (
                                #        ratio, r[wgminr], ratio, r[hgmaxr]))
                                #GpLog.debug(r)
                                return (-1, -1)
                        elif ratio < r[wrminr]:
                                #GpLog.debug(' ratio(%.2f) > r[wrmaxr](%.2f) ' % (ratio, r[wgmaxr]))
                                #GpLog.debug(r)
                                rw = nw
                                rh = rw / ratio
                        elif ratio > r[hrmaxr]:
                                #GpLog.debug(' ratio(%.2f) < r[hrminr](%.2f) ' % (ratio, r[hrminr]))
                                #GpLog.debug(r)
                                rh = nh
                                rw = rh * ratio
                        else:
                                rw = math.sqrt(nmp * ratio)
                                rh = nmp / rw
                return (rw, rh)

	def str2num_(self,str_):
                if str_ == '':
                        return 0
		str_ = str_.lower()
		pos = str_.find('m')
		if pos > 0:
			return int(float(str_[0:pos]) * 1024 * 1024)
		pos = str_.find('k')
		if pos > 0:
			return int(float(str_[0:pos]) * 1024)
		return int(str_)

        #mkdir -p path
        def mkdir_p(self, path):
                try:
                        os.makedirs(path)
                except OSError as exc:  # Python >2.5
                        if exc.errno == errno.EEXIST and os.path.isdir(path):
                                pass
                        else:
                                raise

        def copy_p(self, src, dst):
                try:
                        shutil.copy2(src, dst)
                except OSError as exc:  # Python >2.5
                        print exc.errno
                        if exc.errno == errno.EEXIST:  #OSError: [Errno 17] File exists: '/root/imageprocess/api/out/2m'
                                pass
                        else:
                                raise                                
                if os.path.isfile(dst):
                        GpLog.debug('Successfully copy %s to %s' % (src, dst))                        
                else:
                        raise Exception('error Failed to copy %s to %s' % (src, dst))
                        
        def writeImg(self, path, name, img):
                self.mkdir_p(path)
                absName = path + '/' + name
                img.write(absName)
                GpLog.debug('writed image : ' + absName)
###################################################################	
