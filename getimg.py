#!/usr/bin/python

import subprocess
import sys
import os
import math

from coordCalc import * 
from mapIndex import *
try:
	idxs = loadIdx()
	qs = os.environ["QUERY_STRING"].split("&")
	z=int(qs[0].split("=")[1])
	x=int(qs[1].split("=")[1])
	y=int(qs[2].split("=")[1])
	deg = num2deg(x,y,z)
	ch = WGStoCH(deg[0],deg[1])
	if z > 14:
		st = "pk25"
	elif z > 12:
		st = "pk50"
	elif z > 10:
		st = "pk100"
	else:
		st = "pk500"
	degNext = num2deg(x+1,y+1,z)
	chNext = WGStoCH(degNext[0],degNext[1])
	mps = idxs[st].lookupWGS(deg[0],deg[1],degNext[0],degNext[1])
	if len(mps) > 0:
		if len(mps) > 1:
			mps = sorted(mps,key=lambda mp:mp.coverCH(ch[0],chNext[0],ch[1],chNext[1]))
		mp = mps[-1]
		origPixX =  (chNext[0] - ch[0]) / mp.xRes 
		origPixY =  (chNext[1] - ch[1]) / mp.yRes 
		scaleX = 25600 / origPixX
		scaleY = 25600 / origPixY
		origPixX = math.ceil(origPixX)
		origPixY = math.ceil(origPixY)
		fn = mp.fileName
		xoff = int((ch[0] - mp.xStart) / mp.xRes)
		yoff = int(mp.yPix + (ch[1] - mp.yStart) / mp.yRes)
		xoffR = xoff
		yoffR = yoff
		xpage = 0
		ypage = 0
		if xoff < 0:
			xpage = -xoff
			origPixX += xoff
			xoff = 0
		if yoff < 0:
			ypage = -yoff;
			origPixY += yoff
			yoff = 0
		if xoff > mp.xPix:
			xoff = mp.xPix
		if yoff > mp.yPix:
			yoff = mp.yPix
		if xpage > 0 or ypage > 0:
			page = ["-gravity","SouthEast","-extent","%dx%d"%(origPixX+xpage,origPixY+ypage)]
		else:
			page = []
		pic = []
#		txt = "%g/%g\\n%d/%d\\n%s\\noff:%d/%d\\nscl:%.3g/%.3g\\n%d/%d" % (deg[0],deg[1],int(ch[0]),int(ch[1]),fn,xoffR,yoffR,scaleX,scaleY,int(chNext[0]),int(chNext[1]))
#		txt+="\\n" + ",".join(["%d" % m.coverCH(ch[0],chNext[0],ch[1],chNext[1]) for m in mps])
#		raise BaseException(" ".join(["convert",fn,"-crop","%dx%d+%d+%d" % (origPixX,origPixY,xoff,yoff)]+page+[
#				"-fill","blue","-font","AvantGarde-Book","-gravity", "NorthWest","-pointsize", "30","-annotate","+%d+%d" % (xoff+10,yoff+10), txt,
#				"-scale","%g%%x%g%%" % (scaleX,scaleY),				
#				"-size","256x256",
#			"-quality","75","jpeg:-"]))
		pr = subprocess.Popen(["convert",fn,"-crop","%dx%d+%d+%d" % (origPixX,origPixY,xoff,yoff)]+page+[
#				"-fill","blue","-font","AvantGarde-Book","-gravity", "NorthWest","-pointsize", "30","-annotate","+%d+%d" % (xoff+10,yoff+10), txt,
				"-scale","%g%%x%g%%" % (scaleX,scaleY),				
				"-size","256x256",
			"-quality","75","jpeg:-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	else:
		fn = "None"
		pr = subprocess.Popen(["convert","-size","256x256","xc:white","-fill","blue","-font","Helvetica-Bold","-gravity",
				"NorthWest","-pointsize", "30","-annotate","+10+10","not in\\n"+"\\n".join(qs) + 
			"\\n%g/%g\\n%d\\n%d\\n%s" % (deg[0],deg[1],int(ch[0]),int(ch[1]),fn),
		"-quality","75","jpeg:-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	err = pr.stderr.read(8192)
except:
	print("Content-Type: text/plain\n")
	raise

if len(err) > 0:
	print("Content-Type: text/plain\n")
	print err
	for chunk in iter(lambda: pr.stderr.read(8192), ''): 
		sys.stdout.write(chunk);
else:
	p = pr.stdout
	print("Content-Type: image/jpeg\n")
	for chunk in iter(lambda: p.read(8192), ''): 
		sys.stdout.write(chunk);
