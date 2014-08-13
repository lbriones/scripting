#!/usr/bin/env python
import os
import time
import urllib2
import urllib
import socket
import json

#--------------------------------------
timeout = 4
#--------------------------------------

def login():
    process_ws  = 'http://drupal/test/api/user/login' 
    
    try:
        values  = { 'username' : 'lbriones',
                    'password' : '123456789',
                    'form_id' : 'user_login'
                    }
        data        = urllib.urlencode(values)
        req         = urllib2.Request(process_ws, data)
        auth        = urllib2.urlopen(req, None, timeout = timeout)
        data_return = auth.read()
        cookie      = json.loads(data_return).get('session_name')+'='+json.loads(data_return).get('sessid')
        headerdata  = {'Cookie' : ''+cookie+''}
        req2        = urllib2.Request('http://drupal/test/api/node', None, headerdata)
        response2   = urllib2.urlopen(req2, None, timeout = timeout)
        pagina      = response2.read()
        salida      = json.loads(pagina)
        for i in salida:
            print i.items()

    except urllib2.HTTPError, e:
        print e.code
        
    except urllib2.URLError, e:
        print e
    except Exception as e:
        print e

login()
