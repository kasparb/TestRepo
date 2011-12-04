#!/usr/bin/python

import glob
import os
import sys
import subprocess
import re
from coordCalc import * 
import pickle

class MapTile:
	def __init__(self,xStart,xEnd,xRes,yStart,yEnd,yRes,fn,xPix,yPix):
		if xStart > xEnd:
			(xStart, xEnd) = (xEnd, xStart) 
		if yStart > yEnd:
			(yStart, yEnd) = (yEnd, yStart) 
		self.xStart = xStart
		self.xEnd = xEnd
		self.xRes = xRes
		self.yStart = yStart
		self.yEnd = yEnd
		self.yRes = yRes
		self.fileName = fn
		self.xPix=xPix
		self.yPix=yPix
	def calcWGS(self):
		st = CHtoWGS(self.xStart,self.yStart)
		en = CHtoWGS(self.xEnd,self.yEnd)
		if st[0] < en[0]:
			self.xStartWGS = st[0]
			self.xEndWGS = en[0]
		else:
			self.xStartWGS = en[0]
			self.xEndWGS = st[0]
		if st[1] < en[1]:
			self.yStartWGS = st[1]
			self.yEndWGS = en[1]
		else:
			self.yStartWGS = en[1]
			self.yEndWGS = st[1]
	def isInCH(self,x,y):
		return x >= self.xStart and x <= self.xEnd and y >= self.yStart and y <= self.yEnd
	def isInWGS(self,x,y):
		return x >= self.xStartWGS and x <= self.xEndWGS and y >= self.yStartWGS and y <= self.yEndWGS
	def coverCH(self,xStart,xEnd,yStart,yEnd):
		def cov(s1,e1,s2,e2):
			if s1 > e2 or e1 < s2:
				return 0
			if s1 < s2 and e2 < e1:
				return e2 - s2
			if s2 < s1 and e1 < e2:
				return e1 - s1
			if s1 < s2:
				return e1 - s2
			if s2 < s1:
				return e2 - s1
			raise BaseException()			
		if xStart > xEnd:
			(xStart, xEnd) = (xEnd, xStart) 
		if yStart > yEnd:
			(yStart, yEnd) = (yEnd, yStart) 
		return cov(self.xStart,self.xEnd,xStart,xEnd) * cov(self.yStart,self.yEnd,yStart,yEnd)

	def __repr__(self):
		return "%10g,%10g->%10g,%10g : %s" % (self.xStart,self.yStart,self.xEnd,self.yEnd,self.fileName)

class MapIndex:

	def __init__(self,dr):
		self.index = []
		self.dir = dr
	def add(self,xStart,xEnd,xRes,yStart,yEnd,yRes,fnName,xPix,yPix):
		self.index.append(MapTile(xStart,xEnd,xRes,yStart,yEnd,yRes,fnName,xPix,yPix))
	def __repr__(self):
		return "\n".join([repr(i) for i in self.index])
	def calcWGS(self):
		for i in self.index:
			i.calcWGS()
	def lookupWGS(self,x,y,xEnd,yEnd):
		al = []
		for i in self.index:
			in1 = i.isInWGS(x,y) 
			in2 = i.isInWGS(x,yEnd) 
			in3 = i.isInWGS(xEnd,y) 
			in4 = i.isInWGS(xEnd,yEnd)
			if in1 and in2 and in3 and in4:
				return [i]
			elif in1 or in2 or in3 or in4:
				al.append(i)
		return al
	def lookupCH(self,x,y,xEnd,yEnd):
		al = []
		for i in self.index:
			in1 = i.isInCH(x,y) 
			in2 = i.isInCH(x,yEnd) 
			in3 = i.isInCH(xEnd,y) 
			in4 = i.isInCH(xEnd,yEnd)
			if in1 and in2 and in3 and in4:
				return [i]
			elif in1 or in2 or in3 or in4:
				al.append(i)
		return al

def buildIndex(dr):
	sRe = re.compile("([0-9]+)x([0-9]+)")
	mi = MapIndex(dr)
	for tfw in sorted(glob.glob(os.path.join(dr,"*.tfw"))):
		tif = os.path.splitext(tfw)[0] + ".tif"
		c = subprocess.Popen(["identify",tif],stdout=subprocess.PIPE).communicate()
		m = sRe.search(c[0])
		xLines = int(m.group(1))
		yLines = int(m.group(2))
		tfwF = open(tfw,"r")
		xRes = float(tfwF.readline());
		tfwF.readline()
		tfwF.readline()
		yRes = float(tfwF.readline());
		xPos = float(tfwF.readline());
		yPos = float(tfwF.readline());
		xStart = xPos
		xEnd = xPos + xRes * xLines
		yStart = yPos
		yEnd = yPos + yRes * yLines
		mi.add(xStart,xEnd,xRes,yStart,yEnd,yRes,tif,xLines,yLines)
		print(tif)
#		print "%g->%g %g->%g" % (xStart,xEnd,yStart,yEnd)	
		#print "%g %g %g/%g %g %g" %(xLines,xRes,xPos,yLines,yRes,yPos)
	return mi

def loadIdx():
	i = open("map-index","r")
	idxs = pickle.load(i)
	i.close()
	return idxs

if __name__ == '__main__':
	if sys.argv[1] == "list":
		idxs = loadIdx()
		for i in idxs:
			print "%s:\n%s" % (idxs[i].dir, repr(idxs[i]))
		print("bern:")
		print(idxs['pk25'].lookupCH(600000,200000,600000,200000)) #bern
 #		print("zh:")
#		print(idxs['pk25'].lookupWGS(47.366667,8.55,47.366667,8.55)) #zh
	else:
		idxs = {}
		for i in sys.argv[1:]:
			idx = buildIndex(i)
#			idx.calcWGS()
			idxs[os.path.basename(i)] = idx
	
		o = open("map-index","w")
		pickle.dump(idxs,o)
		o.close()

#	idx.CHtoWGS()
#	print(idx)
	

