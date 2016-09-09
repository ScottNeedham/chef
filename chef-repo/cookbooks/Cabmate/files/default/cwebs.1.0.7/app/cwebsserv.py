# coding=utf-8
from gevent import monkey; monkey.patch_all()
import gevent 
import datetime
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import json
import sys, os
import time
import socket
import thread



app_dir = os.path.dirname(__file__) + "/.."
sys.path.append (app_dir )

import socketcli
import zqqwrap
import smalldb
import config.cwebsconf as Config
import dblayer
import validpr
import driver
import vehicle
import msgconf
import cabmsg
import struct
import sanity_check
import scap
import errormsg as ErrorMsg
import vehicle_msg
import server_utils as Utils
import supervisor_message as SupervisorMsg
import cabmate_messenger

import api_funcs as api_funcs
import scap_funcs

import fares.fare_funcs as fare_funcs


from zones.zone_cache import zone_cache

from controllers import app,  sockcli

import config.local_settings as LocalSettings



sanity_checkup = sanity_check.sanity_check()
if sanity_checkup == 1:
    print 'CWEBS is not configured to receive broadcasts'
    print 'verify contents of /data/itaxisrv_ip.fl'
    sys.exit(0)
elif sanity_checkup == 0:
    print 'CWEBS might be configured to receive broadcasts'
    print 'verify contents of /data/itaxisrv_ip.fl'
else:
    print 'Unable to determine if CWEBS configured to receive broadcasts'
    print 'contact engineering...'


#########################################################################
#APPLICATION START
#########################################################################
def mainloop(): 
    #receive_server_response       

    try:
        import threading

       
        '''
        ths = []
        th1 = gevent.spawn(sockcli.receive_server_response)
        th2 = gevent.spawn(sockcli.socket_reconnect)
        ths = [th1, th2]
        '''

        #th3 = gevent.spawn(cabmsg.gmsg_main)
             
        thread.start_new_thread(sockcli.receive_server_response, ())
        #thread.start_new_thread(sockcli.socket_reconnect, ())
      
        

        '''
        th1 = threading. Thread   (target=sockcli.receive_server_response).start()
        th2 = threading. Thread   (target=sockcli.socket_reconnect) . start()   
        '''        


        run(app, host=LocalSettings.BOTTLE_IP, port=LocalSettings.BOTTLE_PORT, reloader=Config.BOTTLE_AUTO_RELOAD, debug=Config.BOTTLE_DEBUG, server=Config.BOTTLE_SERVER) 
        

        #th4= threading. Thread  (target=run, args=(app,) , kwargs=dict(host=Config.BOTTLE_IP, port=Config.BOTTLE_PORT, reloader=Config.BOTTLE_AUTO_RELOAD, debug=Config.BOTTLE_DEBUG, server=Config.BOTTLE_SERVER)).start()

        while True:
            gevent.sleep(0)  
            #gevent.joinall(ths)
       
    except Exception as e:
       print 'mainloop Exception %s ' % ( str(e) )

    try:
        
        sockcli.sockobj.shutdown(socket.SHUT_RDWR)
        sockcli.sockobj.close()   
    except Exception as e:
       print 'mainloop exit Exception %s ' % ( str(e) )
        
if __name__ == "__main__":
    while True:
        try:
            mainloop()
        except Exception as e:
           print 'main Exception %s ' % ( str(e) )

