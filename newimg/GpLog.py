#! /usr/bin/python
# -*- coding: utf-8 -*-

def isDebug():
    return True

def debug(msg):
    if isDebug():
        print 'debug: %s' % msg

def error(msg):
    print 'error: %s' % msg
