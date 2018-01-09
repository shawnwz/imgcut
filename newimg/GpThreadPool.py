#! /usr/bin/python
# -*- coding: utf-8 -*-

import Queue,  traceback
from threading import Thread

class Worker(Thread):
	def __init__(self, workQueue, timeout=60):
		Thread.__init__(self)
		self.timeout = timeout
		self.setDaemon(True)
		self.workQueue = workQueue
		self.start()

	def run(self):
		while True:
			try:
				func, args, kwargs = self.workQueue.get(timeout=self.timeout)
				func(*args,**kwargs)
			except Queue.Empty:
				print 'queue is empty'
				break
			except Exception,ex:
				print traceback.format_exc()
				raise

class ThreadPool:
	def __init__(self, numOfQueue=1000, numOfThreads=5):
		self.workQueue = Queue.Queue(numOfQueue)
		self.threads = []
		self.numOfThreads = numOfThreads		

	def startThreads(self):
		for i in range(self.numOfThreads):
			thread = Worker(self.workQueue)
			self.threads.append(thread)
	
	def stopThreads(self):
		for thread in self.threads:			
			thread.stop()
		del self.threads[:]

	def addJob(self, func, *args, **kwargs):
		self.workQueue.put( (func,args,kwargs))

	def waitForComplete(self):		
		while len(self.threads):
			thread = self.threads.pop()			
			if thread.isAlive():
				thread.join()

