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
		def getView(mp):
			origPixX =  (chNext[0] - ch[0]) / mp.xRes 
			origPixY =  (chNext[1] - ch[1]) / mp.yRes 
			origPixX = math.floor(origPixX+0.5)
			origPixY = math.floor(origPixY+0.5)
			xoff = int((ch[0] - mp.xStart) / mp.xRes)
			yoff = int(mp.yPix + (ch[1] - mp.yStart) / mp.yRes)
			return (origPixX,origPixY,xoff,yoff)
#		txt="\\n".join(["%d:%g/%g" % (m.coverCH(ch[0],chNext[0],ch[1],chNext[1]),m.xStart,m.yStart) for m in mps])
#		txt+="\\n" + "\\n".join(qs)
#		txtCall = ["-undercolor","lightblue","-fill","blue","-font","AvantGarde-Book","-gravity", "NorthWest",
#			"-pointsize", "30","-annotate","+%d+%d" % (10,10), txt];
		if len(mps) == 1:
			(origPixX,origPixY,xoff,yoff) = getView(mps[0])
			mapCall = [
#					mps[0].fileName,"-crop","%dx%d%+d%+d!" % (origPixX,origPixY,xoff,yoff),
					"-page","%dx%d%+d%+d"%(origPixX,origPixY,-xoff,-yoff), mps[0].fileName,
					"-flatten",
				];
		else:
			(origPixX,origPixY,xoff,yoff) = getView(mps[0])
			mapCall = ["-page","%dx%d%+d%+d"%(origPixX,origPixY,-xoff,-yoff), mps[0].fileName]
			for mp in mps[1:]:
				(origPixX,origPixY,xoff,yoff) = getView(mp)
				mapCall += ["-page","%+d%+d"%(-xoff,-yoff), mp.fileName]
			mapCall += ["-flatten"];

	
		call = ["convert"]+mapCall+[ #txtCall+
			"-resize","256x256!",
			"-quality","75","jpeg:-"]


#		raise BaseException("origPixX=%d origPixY=%d xoff=%d yoff=%d\n%s\n%s" % (origPixX,origPixY,xoff,yoff,txt," ".join(call)))	
		pr = subprocess.Popen(call,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
