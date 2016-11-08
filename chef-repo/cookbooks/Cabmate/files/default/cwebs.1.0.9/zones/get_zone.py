   # coding=utf-8
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import gevent 
import datetime

import json
import sys
import time
import struct
import socket
import thread

import socketcli
import format_field
import msgconf
import cabmsg
import config.cwebsconf as Config
import scap
import server_utils as Utils
import errormsg as ErrorMsg

from zones.zone_cache import zone_cache as zonecache
from zones.zone import ZoneInfo
from fares import itcli

def _get_zone(sockcli, zonecache=None):
    try:
        response = Utils.prepare_header('_get_zone', "default")
        if response.status == 401:
            return

        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__,
            str(order_dic) ))
        except Exception as e:
            print 'Exception: ', str(e)

            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)   

        zone_info = {}
        zone_info['zone'] = -1               
     
       
        response.status = 500
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR       
        zone = -1
        fleet = -1
        try:
            zone, leadtime, lat, lon , fleet = zone_in_cache(zonecache, order_dic)

        except Exception as e:
            sys.stdout.write("%s: Exception 1 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 

        if zone > 0 :
            response.status = 200
            resp_message = "success"
            res = {"status": response.status, "result": {"message": resp_message, "zone": zone , "lead_time": leadtime}}   
            return Utils.make_error_response(response, response.status, resp_message, res)

        try:
            SeqNo = socketcli. sClient.generate_seqno()
            zone_info = ZoneInfo(order_dic, SeqNo)
       
            sys.stdout.write("%s: new zone is created with SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  SeqNo) ) 
      
        except Exception as e:
            sys.stdout.write("%s: _get_zone Exception 2 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, response.status, resp_message, res)            

        #print ' fleet ='  , fleet
        #print repr(zone_info)
        try:
            packed_data, size_data, errmsg = zone_info.info_to_bin()

            zone, leadtime, seqno, resp_message, no_resp = get_zone(packed_data, size_data, errmsg,  SeqNo ) 
           
            if zone > 0:
                try:                  
                    zonecache.add_entry (lat, lon, zone, fleet, leadtime )
                    zonecache.list()
                except Exception as e:
                    sys.stdout.write("%s: Exception 3 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 

            if no_resp > -1:
                response.status = 200
                resp_message = "success"            
                res = {"status":  response.status, "result": {"message":  resp_message, "zone": zone , "lead_time": leadtime}}                        
            else:                   
                errmsg = "Could not get zone"           
                res = {"status":  response.status, "result": {"message":  resp_message, "zone": zone , "lead_time": leadtime}}             
        except Exception as e:
            sys.stdout.write("%s: _get_zone Exception 4 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )


        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "zone": zone , "lead_time": leadtime}}   

        sys.stdout.write("%s: returning out of handler _get_zone ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
        

        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        sys.stdout.write("%s: _get_zone Exception 5 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )        
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)



def get_zone(packed_data, size_data, errmsg, SeqNo):
    zone=-1
    leadtime= seqno=-1
    resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
    no_resp = -1

    dest = msgconf.TFC
    mt = msgconf. MT_GET_ZONE_BY_LAT_LONG
    if errmsg == None :
        base_fmt = 'I I I I I B B B B'                   
        ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )            
        cabmsg.gmsg_send(packed_data, size_data, dest , 0, mt , ss_data, msgconf.CWEBS)

        sys.stdout.write("%s: MT_GET_ZONE_BY_LAT_LONG message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 

        m = None
        sleep_counter=0
        try:                
            while sleep_counter <  Config.QueueTimeoutDic["default"]:
                m = cabmsg.gmsg_rcv2()              
                #print 'Counter ==> ', sleep_counter
                #if m != None and len(m) > 0:
                #    break
                if m != None and len(m) >= 3:
                    print 'Received response ==> ', m, ' sleep_counter = ' , sleep_counter     
                    if m[3] == msgconf. MT_GET_ZONE_BY_LAT_LONG and  m[38] == SeqNo:                            
                        no_resp=0
                        leadtime =  m[12]
                        zone = m[19]
                        seqno = m[38]
                        resp_message = "success"
                    
                        res = {"status": response.status, "result": {"message": resp_message, "job_number": -1, "fare_type": -1,"zone": zone, }}                        
                        break;
                        
                    if m[3] == msgconf. MT_GET_ZONE_BY_LAT_LONG and  m[38] != SeqNo:     
                        print 'Received response with another SeqNo ==> ', m, ' SeqNo = ' ,    m[38]                         
                        no_resp=0
                        leadtime =  m[12]
                        zone = m[19]
                        seqno = m[38]
                        resp_message = "success"
                    
                        res = {"status": response.status, "result": {"message": resp_message, "job_number": -1, "fare_type": -1,"zone": zone, }}                        
                        

                    elif m[3] == msgconf.MT_OP_ERR and m[12] == SeqNo :                                                                        
                        no_resp=0
                        response.status = 200                         
                        if m[10] == ErrorMsg.TFC_ZONE_ERRNO:
                            resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                        else:
                            resp_message = m[13][:31]                            
                        break
                        

                gevent.sleep(1)
                sleep_counter +=1

        except Exception as e:
            sys.stdout.write("%s: get_zone : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         


    sys.stdout.write("%s: get_zone : %d %d %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone, leadtime, seqno ) )             
    return  zone, leadtime, seqno, resp_message, no_resp


def zone_in_cache(zonecache, dic):
    try :
        lat = -1
        lon = -1
        fleet = -1
        zone = -1
        leadtime = -1

        if 'fleet' in dic:
            fleet = int ( dic["fleet"])
        elif 'fleet_number' in dic:
            fleet = int ( dic["fleet_number"])     

        if dic.has_key("lat"):
            lat = str (  dic["lat"] )
        if dic.has_key("lon"):
            lon = str (  dic["lon"] ) 

        if lat == -1  and dic.has_key("pick_up_lat"):
            lat = str (  dic["pick_up_lat"] )
        if lon == -1 and dic.has_key("pick_up_lng"):
            lon = str (  dic["pick_up_lng"] )  

        if lat != -1 and lon != -1 and fleet != -1:
               
            v = zonecache.get( (lat, lon, fleet))

            if v != None:
                print ' v = %d %d ' % (v)
                zone = v[0]
                leadtime = v[1]

    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 

    sys.stdout.write("%s: zone_in_cache  : zone=%d leadtime=%d\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone, leadtime) ) 
    return zone, leadtime, lat, lon , fleet

