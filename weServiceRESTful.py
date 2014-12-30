#!/usr/bin/env python
import commands
import time
import urllib
import json
import socket
import urllib2
import base64
import os
import gzip
import sys
"""
---------------------------------------
requirements
---------------------------------------
#process traffic
python version  : >= 2.6
install         : ethtool
crontab -e      : '* * * * * ws.py traffic'
configuration   : ws.conf 

#process vodstats.sh
ws.py vodstats /path/11-12-2014-16:40:12.json.gz

---------------------------------------
"""

class Ws:
	def authentication(self, url_auth, auth):
		try:
			auth	= json.dumps(auth)
			req		= urllib2.Request(url_auth)
			req.add_header('Content-type', 'application/json')
			req.add_data(auth)
			response= urllib2.urlopen(req)
			r		= json.load(response)
			cookie	= r.get('session_name')+'='+r.get('sessid')
			cookie_token= r.get('token')
			headers	= {"Cookie":""+cookie.encode('ascii','ignore')+"", "Content-type":"application/json","Accept":"text/plain", "X-CSRF-Token":""+cookie_token.encode('ascii','ignore')+""}
			f=open(cookie_file,'w+')
			f.write(str(json.dumps(headers)))
			f.close()
			return response.getcode()

		except urllib2.HTTPError as e:
			print e.code, 'authentication'

	def vodstats(self, logfile, host_service, cookie_file, auth):
		url_login		= 'http://'+host_service+'/api-v1/user/login.json'
		service_vodstats= 'http://'+host_service+'/api-v1/vod_http_stats'
		try:
			if not os.path.isfile(cookie_file):
				authentication = Ws()
				authentication.authentication(url_login, auth)
			data_gz=open(logfile,'rb').read()
			f=open(cookie_file,'r')
			headers	= json.loads(f.read())
			cookie	= headers.get('Cookie')
			cookie_token= headers.get('X-CSRF-Token')
			f.close
			data_encode	= base64.b64encode(data_gz)
			req 		= urllib2.Request(service_vodstats)
			req.add_header('Cookie', cookie)
			req.add_header('Content-type', 'application/json')
			req.add_header('X-CSRF-Token', cookie_token)
			req.add_data('{"data":"'+data_encode+'"}')
			req.get_method = lambda: 'POST'
			response       = urllib2.urlopen(req)
			if json.load(response).get('status') == 'OK':
				if os.path.isfile(logfile):
					os.remove(logfile)
					print 'OK', 'vodstats'

		except urllib2.HTTPError as e:
			if e.code == 403:
				authentication = Ws()
				authentication.authentication(url_login, auth)
				f=open(cookie_file,'r')
							headers = json.loads(f.read())
							cookie  = headers.get('Cookie')
							cookie_token= headers.get('X-CSRF-Token')
							f.close
							data_encode     = base64.b64encode(data_gz)
							req             = urllib2.Request(service_vodstats)
							req.add_header('Cookie', cookie)
							req.add_header('Content-type', 'application/json')
							req.add_header('X-CSRF-Token', cookie_token)
							req.add_data('{"data":"'+data_encode+'"}')
							req.get_method = lambda: 'POST'
							response       = urllib2.urlopen(req)
							if json.load(response).get('status') == 'OK':
									if os.path.isfile(logfile):
											os.remove(logfile)
											print 'OK', 'vodstats'
			else:
				print e.code, 'vodstats'

	def traffic_procdata(self):
		data_old_tx        = {}
		data_old_rx        = {}
		data_new_tx        = {}
		data_new_rx        = {}
		trafico_s_tx       = []
		trafico_s_rx       = []
		result_tx          = {}
		result_rx          = {}
		traffic_total_tx   = {}
		traffic_total_rx   = {}
		try:
			for i in range(60):
				var_traffic_tx_old = commands.getoutput("cat /proc/net/dev | grep eth | sed -e 's/\s\+/|/g' | sed -e 's/\:\+/|/g' | sed -e 's/||\+/|/g' |cut -d '|' -f 2,11").split('\n')
				for j in range(len(var_traffic_tx_old)):
					data_old_tx[var_traffic_tx_old[j].split('|')[0]] = long(var_traffic_tx_old[j].split('|')[1])
				
				var_traffic_rx_old = commands.getoutput("cat /proc/net/dev | grep eth | sed -e 's/\s\+/|/g' | sed -e 's/\:\+/|/g' | sed -e 's/||\+/|/g' |cut -d '|' -f 2,3").split('\n')
				for j in range(len(var_traffic_rx_old)):
					data_old_rx[var_traffic_rx_old[j].split('|')[0]] = long(var_traffic_rx_old[j].split('|')[1])
				
				time.sleep(1)
				
				var_traffic_tx_new = commands.getoutput("cat /proc/net/dev | grep eth | sed -e 's/\s\+/|/g' | sed -e 's/\:\+/|/g' | sed -e 's/||\+/|/g' |cut -d '|' -f 2,11").split('\n')
				for j in range(len(var_traffic_tx_new)):
					data_new_tx[var_traffic_tx_new[j].split('|')[0]] = long(var_traffic_tx_new[j].split('|')[1])
				
				var_traffic_rx_new = commands.getoutput("cat /proc/net/dev | grep eth | sed -e 's/\s\+/|/g' | sed -e 's/\:\+/|/g' | sed -e 's/||\+/|/g' |cut -d '|' -f 2,3").split('\n')
				for j in range(len(var_traffic_rx_new)):
					data_new_rx[var_traffic_rx_new[j].split('|')[0]] = long(var_traffic_rx_new[j].split('|')[1])
				
				trafico_s_tx.append(dict((k,data_new_tx[k] - data_old_tx[k]) for k in data_new_tx if k in data_old_tx));
				trafico_s_rx.append(dict((k,data_new_rx[k] - data_old_rx[k]) for k in data_new_rx if k in data_old_rx));

			for i in trafico_s_tx:
				for j in i:
					if j not in result_tx:
						result_tx[j] = []
					result_tx[j].append(i[j])

			for i in trafico_s_rx:
				for j in i:
					if j not in result_rx:
						result_rx[j] = []
					result_rx[j].append(i[j])

			for i in result_tx:
				traffic_speed = commands.getoutput('/sbin/ethtool '+i+'|grep Speed|sed "s/[a-zA-Z.\:\!\/+]//g"').strip()
				if traffic_speed != '':
					traffic_total_tx[i] = [sum(result_tx[i]) / len(result_tx[i]), long(traffic_speed)]
				else:
					traffic_total_tx[i] = [sum(result_tx[i]) / len(result_tx[i]), long(0)]

			for i in result_rx:
				traffic_speed = commands.getoutput('/sbin/ethtool '+i+'|grep Speed|sed "s/[a-zA-Z.\:\!\/+]//g"').strip()
				if traffic_speed != '':
					traffic_total_rx[i] = [sum(result_rx[i]) / len(result_rx[i]), traffic_total_tx[i][0], long(traffic_speed)]
				else:
					traffic_total_rx[i] = [sum(result_rx[i]) / len(result_rx[i]), long(0), long(0)]

			return traffic_total_rx
		except:
			print 'error, traffic_procdata'

	def traffic_sendata(self, host_service, cookie_file, hostname, auth):
		url_login		= 'http://'+host_service+'/api-v1/user/login.json'
		service_traffic	= 'http://'+host_service+'/api-v1/server/'+hostname
		traffic_procdata = Ws()
		traffic_data = traffic_procdata.traffic_procdata()
		print traffic_data
		try:
			if not os.path.isfile(cookie_file):
				authentication = Ws()
				authentication.authentication(url_login, auth)
			if traffic_data == 'NOK':
				print traffic_data
			else:
				f=open(cookie_file,'r')
				headers	= json.loads(f.read())
				cookie	= headers.get('Cookie')
				cookie_token= headers.get('X-CSRF-Token')
				f.close
				data        = json.dumps(traffic_data)
				req 		= urllib2.Request(service_traffic)
				req.add_header('Cookie', cookie)
				req.add_header('Content-type', 'application/json')
				req.add_header('X-CSRF-Token', cookie_token)
				req.add_data(data)
				req.get_method = lambda: 'PUT'
				response       = urllib2.urlopen(req)
				print json.load(response)

		except urllib2.HTTPError, e:
			authentication = Ws()
			authentication.authentication(url_login, auth)
			if (e.code == 401) or (e.code == 403):
				print e, e.code, 'traffic_sendata'

		except:
			authentication = Ws()
			authentication.authentication(url_login, auth)
			print "error:", sys.exc_info()

services_conf	= '/etc/ws.conf'
cookie_file		= '/tmp/ws.cookie'
hostname		= socket.gethostname()
f=open(services_conf,'r')
config			= json.loads(f.read())
password		= config.get(hostname)
host_service	= config.get('host')
f.close
auth			= {"username":hostname,"password":password}

services = Ws()
if sys.argv[1] == 'vodstats':
	services.vodstats(sys.argv[2], host_service, cookie_file, auth)
elif sys.argv[1] == 'traffic':
	services.traffic_sendata(host_service, cookie_file, hostname, auth)
else:
	print 'no existe un proceso para este parametro'
