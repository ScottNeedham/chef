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
from msg_containers.fare_container import  retrieve_pickup_zone

from fares.fare_fis import FareFis

def _dispatch_save_book_order_tfc(sockcli, zonecache):
    try:
        response = Utils.prepare_header('dispatch_save_book_order_tfc', "default")
        if response.status == 401:
            return

        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            save_order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__,
            str(save_order_dic) ))
        except Exception as e:
            print ' dispatch_save_book_order_tfc Exception: ', str(e)

            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
    
        if not Utils.is_flat_fare(save_order_dic):
            sys.stdout.write("%s: returning 500 because the flat fare is not set \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )                
            response.status = 500
            res["result"] =  {"job_number": -1, "zone": -1}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_FLAT_RATE_NOT_SET, res)            

        #sys.stdout.write("%s: reading pickup datetime\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
        
        lWillCall = False
        try:           
            if save_order_dic.has_key("will_call"):
                if save_order_dic["will_call"] == 'Y':
                    lWillCall = True

            pickup_datetime = None
            if save_order_dic.has_key("pickup_datetime"):
                try:
                    pickup_datetime = datetime.datetime.strptime(
                        save_order_dic["pickup_datetime"], 
                        Config.DateFormat_SaveOrder_Input
                    )
                    #print " 0 type pickup_datetime %s" % ( type(pickup_datetime))           
                except Exception as e:
                    pickup_datetime = Utils.get_server_time()
                    sys.stdout.write(" Exception %s . Default time %s type %s\n" % ( str(e), pickup_datetime, type(pickup_datetime)))                          
                    pass
       
        
            if not lWillCall and "pickup_datetime" not in save_order_dic:
                pickup_datetime = Utils.get_server_time()
                #print " 2 type pickup_datetime %s" % ( type(pickup_datetime))           
                sys.stdout.write("%s: pickup datetime is determined as %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(pickup_datetime)))             
        
        except Exception as e:
            sys.stdout.write("%s: Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))             

        zone = -1
        zone_info = {}
        zone_info['zone'] = zone  
        new_fare=None
        packed_data = None

        #print " 3 type pickup_datetime %s" % ( type(pickup_datetime))           

        if lWillCall and save_order_dic.has_key("pickup_datetime") and save_order_dic.has_key("will_call_expiry_date"):
            save_order_dic['pickup_datetime']=''
            sys.stdout.write(" resetting pickup_datetime %s \n" % ( save_order_dic['pickup_datetime']) ) 

        if Config.lTryZoneItaxisrv:
            if "force_zone" not in save_order_dic or ("force_zone" in save_order_dic  and save_order_dic["force_zone"] != 'Y'):
                response.status, zone_info, res = Utils.check_zone(sockcli,save_order_dic)          

        if "force_zone" in save_order_dic  and save_order_dic["force_zone"] == 'Y' and 'zone' in save_order_dic:    
            zone_info['zone'] = save_order_dic["zone"]              
 
        if "pick_up_zone" in save_order_dic:
            zone_info["zone"] = save_order_dic["pick_up_zone"]  
            zone =  save_order_dic["pick_up_zone"]  

        try:
            try:
                SeqNo = socketcli. sClient.generate_seqno()
                new_fare =  FareFis (save_order_dic, zone_info["zone"], SeqNo)  #itcli.Fare(save_order_dic, zone_info["zone"], SeqNo)            
                sys.stdout.write("%s: new fare is created with zone %s SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone_info["zone"], SeqNo) ) 
            except Exception as e:
                sys.stdout.write("%s: save_book_order_tfc 1 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 
                return Utils.make_error_response(response, 500,str(e))  
            try:
                print ' ==== fare_to_bin ====='

                packed_data, size_data, errmsg = new_fare.fare_to_bin()
            except Exception as e:
                sys.stdout.write("%s: save_book_order_tfc 2 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 
                return Utils.make_error_response(response, 500,str(e))  

            #check if immediate or future
            if "will_call" not in save_order_dic and  "is_future" not in save_order_dic \
                or ( "will_call" in save_order_dic and save_order_dic["will_call"] != "Y" )\
                or ( "future" in save_order_dic and save_order_dic["future"] != "Y" ) :
                if pickup_datetime is not None:
                    try:
                        print ' *** pickup date time is **** %s ' % (  pickup_datetime )


                        #Try immediate for less than default immediate timeout
                        if Config.DefaultZoneTimeout >  0:
                            print " type pickup_datetime %s" % ( type(pickup_datetime))                         

                            if pickup_datetime >  Utils.get_server_time() + datetime.timedelta(minutes=Config.DefaultZoneTimeout) :                                
                                save_order_dic ["is_future"] = "Y"
                                new_fare.fare_set_future(True,  pickup_datetime)
                                print " *** FUTURE 1 *** \n"      

                        else:
                            #1 First check if you can find the zone lead time in the cache
                            if Config.CheckZoneCache is True:
                                zone, leadtime, lat, lon , fleet = zone_in_cache(zonecache, save_order_dic)
                                sys.stdout.write("%s: Found zone=%d lead time=%d \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone, leadtime) )                         
                            
                            if zone > 0 and leadtime > 0:
                                #Found it. now calculate the delta
                                if pickup_datetime >  Utils.get_server_time() + datetime.timedelta(minutes=leadtime) :
                                    save_order_dic ["is_future"] = "Y"
                                    new_fare.fare_set_future(True,  pickup_datetime)
                                    print " *** FUTURE 2 *** \n"      

                                zone_info["lead_time"] = leadtime
                                zone_info["zone"] = zone
                            #2 Retrieve from TFC
                            else:
 
                                zone_info = ZoneInfo(save_order_dic, SeqNo)
                                packed_data, size_data, errmsg = zone_info.info_to_bin()
                                zone, leadtime, seqno, errmsg, no_resp = get_zone(packed_data, size_data, errmsg,  SeqNo ) 
           
                                print ' ***  zone = %d  leadtime %d seqno %s *** ' % ( zone, leadtime, seqno  )
                                SeqNo=None
                                if zone > 0:                             
                              
                                    if pickup_datetime >  Utils.get_server_time() + datetime.timedelta(minutes=leadtime) :                               
                                        save_order_dic ["is_future"] = "Y"
                                        new_fare.fare_set_future(True)
                                        print " *** FUTURE 3 *** \n"      

                                zone_info["lead_time"] = leadtime
                                zone_info["zone"] = zone                                    

                            #Now try the default
                            if "is_future" not in save_order_dic  \
                                and pickup_datetime  >  Utils.get_server_default_immediate_time():
                                    save_order_dic ["is_future"] = "Y"
                                    new_fare.fare_set_future(True)
                                    print " *** FUTURE 4 *** \n"      
                      

                    except Exception as e:
                        sys.stdout.write("%s: save_book_order_tfc 3 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e)) ) 
                        return Utils.make_error_response(response, 500,str(e))                        

        except Exception as e:
            print "dispatch save_book_order_tfc 4: Exception", str(e)
            return Utils.make_error_response(response, 500, str(e))            
                           
        #print 'sending '

        dest = msgconf.TFC
        mt = msgconf. MT_GE_CALL
        fare_type = "immediate"
        job_number = -1
      
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        response.status = 500

        try:       
            if SeqNo is None:
                SeqNo = socketcli. sClient.generate_seqno()
                new_fare =  FareFis(save_order_dic, zone_info["zone"], SeqNo)  #itcli.Fare(save_order_dic, zone, SeqNo)            
                sys.stdout.write("%s: new fare is updated with zone %s SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone_info["zone"], SeqNo) ) 

            try:              
                packed_data, size_data, errmsg = new_fare.fare_to_bin(zone, SeqNo)
                print(' size_data={0} errmsg={1}'.format ( size_data, errmsg) )
            except Exception as e:
                sys.stdout.write("%s: +++ Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) ) 
            
            
            print ' flag is %s lWillCall=%s' % (new_fare.fare_future() , lWillCall)
        
            if lWillCall or save_order_dic.has_key("is_future") and save_order_dic["is_future"] in ['Y', 'y']:  
                print " Trying future .... ?"
                fare_type = "future"
                if zone <= 0:          
                    #zone, leadtime, seqno = get_zone(packed_data, size_data, errmsg,  SeqNo )  #retrieve_zone(packed_data, size_data, errmsg,  SeqNo )        
                    #print ' zone = %d  leadtime %d seqno %s ' % ( zone, leadtime, seqno  )
                    zone_info = ZoneInfo(save_order_dic, SeqNo)
                    packed_data, size_data, errmsg = zone_info.info_to_bin()
                    zone, leadtime, seqno, errmsg, no_resp = get_zone(packed_data, size_data, errmsg,  SeqNo )  
                if zone > 0:
                    SeqNo = socketcli. sClient.generate_seqno()
                    packed_data, size_data, errmsg = new_fare.fare_to_bin(zone, SeqNo)
                    fare_type = "future"
                    dest = msgconf.TIMEMGR
                    mt = msgconf. MT_NEWFARE
                else:    
                    resp_message = errmsg = "Could not get zone"  
                    response.status = 500         
                    res = {"status":  response.status, "result": {"message": errmsg, "job_number": job_number, "zone": zone , "fare_type": fare_type}}            
            else:
                dest = msgconf.TFC
                mt = msgconf. MT_GE_CALL

        except Exception as e:
            print "dispatch save_book_order_tfc 5: Exception", str(e)
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        

        if errmsg == None :
            base_fmt = 'I I I I I B B B B'                   
            ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )            
            cabmsg.gmsg_send(packed_data, size_data, dest , 0, mt , ss_data, msgconf.CWEBS)

            sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 


            m = None
            sleep_counter=0
            try:   
                status = -1
                try:
                    numSecs = Config.QueueTimeoutDic["default"]
                    numIters = int (numSecs/msgconf.Q_TIMESLOT)
                except Exception as e:
                    numIters =  2/msgconf.Q_TIMESLOT

                for sleep_counter in range( numIters ) :                    
                    m = cabmsg.gmsg_rcv2()              
                    #print 'Counter ==> ', sleep_counter
                    #if m != None and len(m) > 0:
                    #    break
                    if m != None and len(m) >= 3:
                        sys.stdout.write("%s:  Received response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if m[3] == msgconf.MT_ENTER_CALL and  m[38] == SeqNo:
                            #print 'Received response  msgconf.MT_ENTER_CALL ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[11])
                            zone = m[19]
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status = 0
                            break;

                        elif m[3] == msgconf.MT_NEWFARE and m[13] == SeqNo:
                            #print 'Received response  msgconf.MT_NEWFARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status = 0                            
                            break;                            
                        
                        elif m[3] == msgconf.MT_OP_ERR and m[12] == SeqNo :   
                            print 'Received response  msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter   
                            if m[10] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrMsg =  ErrorMsg.ERROR_MSG_INVALID_PICKUP_ZONE # ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[13][:31]
                            response.status = 500 
                            status = 0                            
                            break

                    else:
                        #sys.stdout.write("%s: No response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if status < 0:                    
                            gevent.sleep(msgconf.Q_TIMESLOT)                        

            except Exception as e:
                sys.stdout.write("%s: dispatch save_book_order_tfc 6 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        
     
            # Try to recover from zone issues ...
            '''
            r = {}
            if resp_message == ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO:
                try:
                    r = Utils.get_zone_by_gps(sockcli, save_order_dic["pick_up_lat"], save_order_dic["pick_up_lng"], save_order_dic["fleet_number"])
                    if "zone" in r:
                        print ' r ==> ', r
                except Exception as e:
                    sys.stdout.write("%s: dispatch save_book_order_tfc 5 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
            '''    

            if  job_number > -1:    
                ## Try to read the fare if some reaon we cannot get it right
                if zone == 0:
                    zone = retrieve_pickup_zone(job_number, fare_type)

                res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "zone": zone, "fare_type": fare_type}}                       
            else:                
                res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "zone": zone, "fare_type": fare_type}}
            
        else :
            res = {"status":  response.status, "result": {"message": errmsg, "job_number": job_number, "zone": zone , "fare_type": fare_type}}            
     
        #print '!!!returning out of handler'
        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "zone": zone, "fare_type": fare_type}}   

        sys.stdout.write("%s: returning out of handler save_book_order_tfc ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
        

        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        print "dispatch save_book_order_tfc 7: Exception", str(e)
        return Utils.make_error_response(response, 500, str(e))

