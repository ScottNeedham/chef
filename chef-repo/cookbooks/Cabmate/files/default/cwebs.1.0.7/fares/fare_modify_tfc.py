
# coding=utf-8
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import gevent 
import datetime

import json
import sys
import time
import zqqwrap
import smalldb
import socketcli
import socket
import thread
import itcli
import format_field
import dblayer
import validpr
import driver
import vehicle
import msgconf
import cabmsg
import struct

import config.cwebsconf as Config
import scap
import server_utils as Utils
import errormsg as ErrorMsg

from zones.get_zone import zone_in_cache, get_zone

from zones.zone import ZoneInfo



def _dispatch_modify_book_order_tfc(sockcli, data_src_repo , zonecache):
    try:  
   
        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))

        job_number = -1
        zone = -1
        leadtime = -1
        dest = msgconf.TFC
        mt = msgconf. MT_GE_CALL
        fare_type = "immediate"  
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        zone_info = { "zone":  zone, "lead_time": leadtime }      

        try:
            response =  Utils.prepare_header("_dispatch_modify_book_order_tfc", "default")
            sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))        
            if response.status == 401:
                return

        except Exception as e:
                sys.stdout.write("%s: Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) )) 
    
                res["result"] =  {"message": resp_message, 
                                    "job_number": job_number,                                             
                                    "zone": zone}
                return Utils.make_error_response(response, 500, resp_message, res)

        response.headers["Content-type"] = "application/json"

        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            
            order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(order_dic) ))
        except Exception as e:
            sys.stdout.write("%s: Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) )) 

            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            response.status = 500
            return json.dumps(res)

        #print '_dispatch_modify_book_order_tfc ==> ', order_dic
        #####################################################
        # check if fare exists - fare_number[-6:].lstrip('0')
        #####################################################
        if not order_dic.has_key("fare_number"):
            sys.stdout.write("%s: returning 500 because fare_number is invalid\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
            res["result"] =  {"message": resp_message, "job_number": job_number, "fare_number": "", "zone": zone}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, res)
            
                             
        else:
            try:
                fare_num = int(order_dic["fare_number"])
            except Exception as e:
                sys.stdout.write("%s: returning 500 because fare_number is invalid\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
    
                res["result"] =  {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, 
                                              "job_number": job_number, 
                                              "fare_number": order_dic["fare_number"], 
                                              "zone": zone}
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, res)

        if not Utils.is_flat_fare(order_dic):
            sys.stdout.write("%s: returning 500 because the flat fare is not set \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )                
            response.status = 500
            res["result"] =  {"job_number": job_number, "zone": zone}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_FLAT_RATE_NOT_SET, res)               

        
        try:
            lim_fare, lfu_fare, queprio = dblayer.get_fare_number(data_src_repo, order_dic["fare_number"])
        except Exception as e:
            lim_fare, lfu_fare, queprio = False, False, 0

        if lim_fare == False and lfu_fare == True:
            fare_type = "future"

        lWillCall = False
        pickup_datetime = None
        
        try:
            if order_dic.has_key("pickup_datetime"):
                try:
                    pickup_datetime = datetime.datetime.strptime(
                    order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                    )
                except Exception as e:
                    pickup_datetime = Utils.get_server_time()
                    sys.stdout.write("default time %s \n" % (pickup_datetime))
                    pass
            else:
                pickup_datetime = Utils.get_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))

            if order_dic.has_key("will_call"):
                if order_dic["will_call"] == 'Y':
                    lWillCall = True

        except Exception as e:
            sys.stdout.write("%s: Exception 5 %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                         
                       
              
        try:
            fare_type_new = "immediate"
            if not lWillCall  and  pickup_datetime <= Utils.get_server_pickup_time(zone_info):
                fare_type_new = 'immediate'
            elif lWillCall  or  pickup_datetime > Utils.get_server_pickup_time(zone_info):
                fare_type_new = 'future'
        except Exception as e:
            fare_type_new = 'immediate'
            pass


        sys.stdout.write("%s: will call\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )
        
        sys.stdout.write("%s: pickup datetime in mod fare is determined as %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        str(pickup_datetime))) 

        sys.stdout.write("%s: fare type in mod %s is determined\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), fare_type_new))
        sys.stdout.write('fare_type %s, fare_type_new %s \n' % (fare_type, fare_type_new))
        if not lim_fare and not lfu_fare:
            fare_type = fare_type_new 
            if fare_type == "future":
                order_dic["is_future"] = 'Y'

        if lWillCall and order_dic.has_key("pickup_datetime") and order_dic.has_key("will_call_expiry_date"):
            order_dic['pickup_datetime']=''
            sys.stdout.write(" resetting pickup_datetime %s \n" % ( order_dic['pickup_datetime']) ) 


        SeqNo = sockcli.generate_SeqNo()

        ### DO NOT DEFAULT THESE FIELDS ####
        if lim_fare or lfu_fare :
            if (order_dic.has_key("dispatch_priority") and  order_dic["dispatch_priority"] == "") or  "dispatch_priority" not in  order_dic:
                order_dic["dispatch_priority"] = queprio
            print ' que prio in db=%d dico=%s' % ( queprio, order_dic["dispatch_priority"])
     
        ###
        fare_num = order_dic["fare_number"][-6:].lstrip('0')
        SeqNo = socketcli. sClient.generate_seqno()
        new_fare = itcli.Fare(order_dic, zone_info["zone"], SeqNo, fare_num)   
        errmsg=None      
        try:

            #1 First check if you can find the zone lead time in the cache
            if Config.CheckZoneCache is True:
                zone, leadtime, lat, lon, fleet = zone_in_cache(zonecache, order_dic)
                sys.stdout.write("%s: Found zone=%d lead time=%d \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), zone, leadtime) ) 
            if zone > 0 and leadtime > 0:         
                zone_info["lead_time"] = leadtime
                zone_info["zone"] = zone
            #2 Retrieve from TFC
            else:

                zone_info = ZoneInfo(order_dic, SeqNo)
                packed_data, size_data, errmsg = zone_info.info_to_bin()
                zone, leadtime, seqno, errmsg, no_resp = get_zone(packed_data, size_data, errmsg,  SeqNo)                       
                print ' ***  zone = %d  leadtime %d seqno %s *** ' % ( zone, leadtime, seqno)
                SeqNo=None
                if zone > 0:                             
                    zone_info.lead_time = leadtime
                    zone_info.zone = zone 
                    print zone_info
            if zone < 0:
                response.status = 500
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_CANNOT_ZONE, res)

        except Exception as e:
            sys.stdout.write("%s: Exception 4 %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))                         


        sys.stdout.write("%s: modifying an existing fare %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        order_dic["fare_number"])
        ) 


        try:
            response.status,  resp_message, res = send_to_host(new_fare, order_dic, zone, SeqNo, errmsg, lWillCall, fare_num)

        except Exception as e:          
            sys.stdout.write("%s: Exception 6 Could not create Fare object %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            response.headers["Content-type"] = "application/json"
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return json.dumps(res)
 
      
       
        if 'result' in res:
            res['result']['job_number'] = order_dic["fare_number"][-6:].lstrip('0')
            res['result']['fare_type'] = fare_type
        else:
            res['result'] = { "message": resp_message, 'job_number':  order_dic["fare_number"][-6:].lstrip('0'), 'fare_type' :  fare_type}

        res["status"] =  response.status

     
        response.headers["Content-type"] = "application/json"
       
             
        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type, "zone": zone_info["zone"]}}            

        sys.stdout.write("%s: returning out of handler modify_book_order_tfc ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        sys.stdout.write("%s: dispatch modify_book_order_tfc: Exception 7 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)



def send_to_host(new_fare, order_dic, zone, SeqNo, errmsg, lWillCall, fare_num):
    try:
        dest = msgconf.TFC
        mt = msgconf. MT_MODFAREINFO  # immediate mod fare
        fare_type = "immediate"
        job_number = -1
      
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        response.status = 500
        res = {}

        try:
 
            if SeqNo is None:
                SeqNo = socketcli. sClient.generate_seqno()
                new_fare = itcli.Fare(order_dic, zone, SeqNo, fare_num)            
                sys.stdout.write("%s: new fare is updated with zone %s SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone, SeqNo) ) 
        
            packed_data, size_data, errmsg = new_fare.fare_to_bin(zone, SeqNo)
            
            print ' flag is %s lWillCall=%s' % (new_fare.fare_future() , lWillCall)
        
            if lWillCall or order_dic.has_key("is_future") and order_dic["is_future"] in ['Y', 'y']:  
                dest = msgconf.TIMEMGR
                mt = msgconf. MT_UPD_FARE #437
                fare_type = "future"
            else:
                dest = msgconf.TFC
                mt = msgconf. MT_MODFAREINFO 

        except Exception as e:
            print "send_to_host 1: Exception", str(e)
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        

        if errmsg == None :
            base_fmt = 'I I I I I B B B B'                   
            ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )            
            cabmsg.gmsg_send(packed_data, size_data, dest , 0, mt , ss_data, msgconf.CWEBS)

            sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
          
            m = None
           
            try:                
                status=-1
                try:
                    numSecs = Config.QueueTimeoutDic["default"]
                    numIters = int (numSecs/msgconf.Q_TIMESLOT)
                except Exception as e:
                    numIters =  2/msgconf.Q_TIMESLOT                

                for sleep_counter in range(numIters) :
                    m = cabmsg.gmsg_rcv2()              
         
                    if m != None and len(m) >= 3:
                        sys.stdout.write("%s:  Received response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if m[3] == msgconf.MT_ENTER_CALL and  m[38] == SeqNo:
                            print 'Received response  msgconf.MT_ENTER_CALL ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[11])
                            zone = m[19]
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status =0                            
                            break;

                         ### ???? ####
                        if m[3] == msgconf.MT_MODFAREINFO and  m[13] == SeqNo:
                            print 'Received response  msgconf.MT_MODFAREINFO ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[9]) 
                            zone = m[11]                          
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status =0                            
                            break;

                        elif m[3] == msgconf.MT_NEWFARE and m[13] == SeqNo:
                            print 'Received response  msgconf.MT_NEWFARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break;


                        ### ???? ####
                        elif m[3] == msgconf.MT_UPD_FARE and m[13] == SeqNo: 
                            print 'Received response  msgconf.MT_UPD_FARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break


                        elif m[3] == msgconf.MT_OP_ERR and len (m ) >=  10 :   
                            print 'Received response  msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter   
                            if m[9] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[9]
                            response.status = 500 
                            status =0
                            break

                        elif m[3] == msgconf.MT_OP_ERR and len(m) > 12 and  m[12] == SeqNo :   
                            print 'Received response  msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter   
                            if m[10] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[13]
                            response.status = 500 
                            status =0
                            break
                        
                    else:
                        sys.stdout.write("%s:  No response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if status < 0:                    
                            gevent.sleep(msgconf.Q_TIMESLOT)
                      

            except Exception as e:
                sys.stdout.write("%s: dispatch send_to_host 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

        sys.stdout.write("%s: Received response from  %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
        return response.status, resp_message, res
    except Exception as e:
        sys.stdout.write("%s: send_to_host 3 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

