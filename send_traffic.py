#!/usr/bin/env python
import commands
import time
import urllib
import json
import socket

"""
---------------------------------------
requirements
---------------------------------------

python version  : >= 2.6
install         : ethtool
crontab -e      : '* * * * * python /root/traffic.py'
---------------------------------------
"""

hostname        = socket.gethostname()
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
  for i in range(3):
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
    
    var_traffic_rx_new = commands.getoutput("cat /proc/net/dev | grep eth | sed -e 's/\s\+/|/g' | sed -e 's/\:\+/|/g' | sed -e 's/||\+/|/g' |cut -d '|' -f 2,11").split('\n')
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
      traffic_total_rx[i] = [sum(result_rx[i]) / len(result_rx[i]), long(traffic_speed)]
    else:
      traffic_total_rx[i] = [sum(result_rx[i]) / len(result_rx[i]), long(0)]

  traffic_total_tx['hostname'] = hostname
  traffic_total_rx['hostname'] = hostname
  print traffic_total_rx, traffic_total_tx
  #data        = urllib.urlencode(traffic_total)
  #response    = urllib.urlopen('http://domain.com/api/restful', data)

except urllib, e:
  print 'error urllib'

except Exception as e:
  print e
