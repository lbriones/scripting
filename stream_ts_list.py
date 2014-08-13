#!/usr/bin/env python
import os
import urlparse
import urllib2

#--------------------------------------
 
def main(stream):
	conn 		= urllib2.urlopen(stream)
	manifest 	= conn.read()
	playurl 	= urlparse.urlparse(stream)
	mybaseurl 	= os.path.dirname(playurl.path)
	domain 		= playurl.scheme+'://'+playurl.netloc

	for line in manifest.split("\n"):
		line = line.strip()
		if not line.startswith("#EXTM3U") and not line.startswith("#EXT-X-"):
			if not line.startswith("#"):
				fragmentname = os.path.join(mybaseurl, line.split("/")[-1])
				tsplay_url = (domain+''+fragmentname)
				if '.ts' in tsplay_url:
					print tsplay_url

if __name__ == '__main__':
	main('http://domain.com/playlist.m3u8')
