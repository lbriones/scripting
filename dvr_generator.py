#!/usr/bin/python
import json
import math
import time
import os
import sys
import fileinput
import shutil
import re

print sys.argv[1]

if sys.argv[1] != "index.m3u8.bak":
	print "key for execute"
	sys.exit()

time_actual = int(time.time())
TS_PATH 	  = '/hls/public_html/playlist/'
INDEX_PATH 	= '/hls/public_html/live/'

if not os.path.exists(TS_PATH):
	os.makedirs(TS_PATH)

current2	= open(""+INDEX_PATH+"index.m3u8", "r")
last_ts		= current2.readlines()
last_ts		= last_ts[len(last_ts)-5].replace('.ts', '')
last_ts		= int(last_ts)
#first_ts = last_ts[len(last_ts)+1]
current2.close()



current	= open(""+INDEX_PATH+"index.m3u8", "r")
json		= {}
line		= None
header	= []
headers	= []
data		= []
zone		= [0,1800,3600,5400,7200,10800,14400,18000,19800,21600,23400,25200,26100,27000,28800,29700,32400,342
00,36000,37800,39600,40500,41400,43200,44100,45000,46800,48600,49200,50400,52200,54000,54900,55200,55800,57600,58140,59400,61200,630
00,64800,66600,68400,70200,70560,72000,73800,74400,75600,77100,78240,79200,82800,84600]
zone_tmp	= [0,1800,3600,5400,7200,10800,14400,18000,19800,21600,23400,25200,26100,27000,28800,29700,32400,34200,36000
,37800,39600,40500,41400,43200,44100,45000,46800,48600,49200,50400,52200,54000,54900,55200,55800,57600,58140,59400,61200,63000,64800
,66600,68400,70200,70560,72000,73800,74400,75600,77100,78240,79200,82800,84600]
tz			= []
buffers		= []
intervalo	= 16000
tmp_discon 	= []
counter 	= 0
pre 		= ''

for i in reversed(zone_tmp):
	if os.path.isfile(""+TS_PATH+""+str(i)+".m3u8.discon"):
		file = open(""+TS_PATH+""+str(i)+".m3u8.discon","r")
		lines = file.readlines()
		for j, lin in enumerate(lines):
			if "#EXT-X-DISCONTINUITY\n" in lin:
				ts_discontinuity = lines[j+2].replace('../','').replace('.ts','')
				ts_discontinuity = int(ts_discontinuity)
				#for line in current:
				#	if line[0] != '#':
				#		line = int(line.replace('.ts',''))
				if ts_discontinuity > (last_ts-i*1000):
					shutil.copy(TS_PATH+"pre.m3u8", TS_PATH+""+str(i)+".m3u8")
				else:
					os.remove(TS_PATH+""+str(i)+".m3u8.discon")

for line in current:
	line = line.replace('\n', '')
	if len(header) == 0 and ((line.find('#EXTINF:') < 0) and (line.find('#EXT-X-DISCONTINUITY:') < 0)):
		buffers.append(line)
		maximo = []
		data_tmp = []
	else:
		header = buffers
		headers.append(line)
	if line[0] != '#':
		line = int(line.replace('.ts',''))
		for i in reversed(zone):
			cercania = last_ts-i*1000-line
			if cercania <= 0 and counter < 3:
				data.append((last_ts-line))
				data.append(line)
				data.append([])
				data[2].append(str(''.join(headers))+'\n')
				data.append(last_ts-(i*1000))
				data.append(line-(last_ts-i*1000))
				if counter == 0 :
					if data[2][0].split(':')[0] != '#EXT-X-DISCONTINUITY':
						maximo1 = data[2][0].split(':')
						maximo1 = maximo1[1].split(',')[0]
						maximo.append(int(math.ceil(float(maximo1))))
					data[2] = [s.replace('#EXT-X-DISCONTINUITY#EXTINF:', '#EXT-X-DISCONTINUITY\n#EXTINF:') for s
 in data[2]]
					header[3] = re.sub(r'#EXT-X-TARGETDURATION:[0-9]+', '#EXT-X-TARGETDURATION:'+str(max(maximo)
), header[3])
					#header = [x for x in header if x != '#EXTM3U']
					#print header
					f=open(""+TS_PATH+""+str(i)+".m3u8.bak","a")
					f.write(str('\n'.join(header))+'\n#EXT-X-ALLOW-CACHE:NO\n')
					f.close()
				f=open(""+TS_PATH+""+str(i)+".m3u8.bak","a")
				f.write(str('\n'.join(data[2]).split(',')[0]+',')+'\n')
				f.write(str('../'+'\n'.join(data[2]).split(',')[1]))
				f.close()
				counter = counter + 1
				if counter <= 3:
					data_tmp1 = data[2]
					data_tmp.append(str(data_tmp1))
				#if counter == 1 and '#EXT-X-DISCONTINUITY' in data[2][0]:
				#	shutil.copy(TS_PATH+""+str(i)+".m3u8.bak", TS_PATH+""+str(i)+".m3u8")
			if counter == 3:
				if '#EXT-X-DISCONTINUITY' not in data_tmp[0]:
					shutil.copy(TS_PATH+""+str(i)+".m3u8.bak", TS_PATH+""+str(i)+".m3u8")
					f=open(""+TS_PATH+""+str(i)+".m3u8.bak","w+")
					f.truncate()
					f.close()
				else:
					pre = '\n'.join(header)
					pre += '\n#EXT-X-ALLOW-CACHE:NO\n#EXT-X-DISCONTINUITY\n#EXTINF:11.010,\n../0000000000001.ts\
n#EXTINF:11.010,\n../0000000000002.ts\n#EXTINF:11.010,\n../0000000000003.ts'
					#print ''.join(pre)
					f=open(""+TS_PATH+"pre.m3u8","w+")
					f.write(''.join(pre))
					f.close()

					shutil.copy(TS_PATH+""+str(i)+".m3u8.bak", TS_PATH+""+str(i)+".m3u8.discon")
					shutil.copy(TS_PATH+"pre.m3u8", TS_PATH+""+str(i)+".m3u8")
					f=open(""+TS_PATH+""+str(i)+".m3u8.bak","w+")
					f.truncate()
					f.close()

				data_tmp = []
				counter = 0
				maximo = []
				zone.pop()
		headers = []
		data = []
current.close()

#for i in reversed(zone_tmp):
#	shutil.copy(TS_PATH+""+str(i)+".m3u8.bak", TS_PATH+""+str(i)+".m3u8")
