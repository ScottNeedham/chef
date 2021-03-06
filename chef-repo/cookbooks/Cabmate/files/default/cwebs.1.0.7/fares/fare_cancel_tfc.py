
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


from zones.zone import ZoneInfo

from fares.its_event import its_event, future_cancel_event

from msg_containers.fare_container import  fare_container

import msgconf

def _dispatch_cancel_book_order_tfc(sockcli, data_src_repo):
    try:        
        response =  Utils.prepare_header('dispatch_cancel_book_order_tfc', "default")
        if  response.status == 401:
            return            
        response.status = 500
        response.headers["Content-type"] = "application/json"
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR

        res = {"status": response.status, "result": {"message": resp_message } }

        clen = request.content_length
        request.body.seek(0)
        try:
            order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(order_dic) ) )
        except Exception as e:
            print 'Exception ', str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)

        try:
            fare_num = order_dic["fare_number"]
            if len (str(fare_num)) >  6:
                fare_num  = fare_num[-6:].lstrip('0')               
          
            sys.stdout.write("%s: canceling fare number %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), order_dic["fare_number"] ))
        except Exception as e:          
            sys.stdout.write("%s: invalid fare number\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)

 
        fare_type = ''
        if order_dic.has_key("fare_type") and Config.EnableCancelByFareType:
            fare_type = order_dic["fare_type"]                 

            if fare_type in [ "immediate", "future"] :
                job_number = str(fare_num).ljust(6,' ')
              
            try:     
                response.status, resp_message, res = send_cancel_request(sockcli, job_number, fare_type, order_dic, response)

                sys.stdout.write("%s: returning out of handler cancel_book_order_tfc ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
                return Utils.make_error_response(response, response.status, resp_message, res)

            except Exception as e:          
                sys.stdout.write("%s: Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                response.headers["Content-type"] = "application/json"
                response.status = 500
                res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
                return json.dumps(res)
        
        for tab, ft in zip(["farefl", "futfarefl"], ["immediate", "future"]):
            if ft == "immediate":
                fare_num_str = str(fare_num).rjust(7,'0')
                sign_str = "-"
            if ft == "future":
                fare_num_str = "5" + str(fare_num).rjust(6,'0')
                sign_str = "+"
            
            sql_stat = '''select rr.Remark4 as Remark4,
                                 rr.SequenceNumber as SequenceNumber,
                                 rr.FareNumber as FareNumber from %s rr            
               where (
               (`FareNumber` = cast(concat(date_format((now() %s interval 1 day), '%%Y%%m%%d'), '%s') as unsigned)) or
               (`FareNumber` = cast(concat(date_format((now()), '%%Y%%m%%d'), '%s') as unsigned))
               ) limit 1;''' % (tab, sign_str, fare_num_str, fare_num_str)

            try:
                print 'executing ', sql_stat
                info = data_src_repo.fetch_many(sql_stat)
                print 'info ', info
            except Exception as e:
                res["result"] = {"message": ErrorMsg.ERROR_MSG_CABMATEREPO + ": " + Config.DB_HOST_REPO}
                return json.dumps(res)

            for (Remark4, SequenceNumber, FareNumber) in info:
                print 'FareNumber=', FareNumber
                job_number = str(FareNumber)[-6:].lstrip('0').ljust(6,' ')
                print 'job_number=', job_number


                response.status, resp_message, res = send_cancel_request(sockcli, job_number, ft, order_dic, response)

                return Utils.make_error_response( response, response.status, resp_message, res)

               
        res["result"] = {"message": "fare is not found in CabmateRepo DB"}
        return json.dumps(res)
    except Exception as e:
        print '*** Exception 2 ', str(e)
        response.status = 500
        response.headers["Content-type"] = "application/json"
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)  

    return json.dumps(res)

def send_cancel_request(sockcli, job_number, fare_type, order_dic, response):

    try:
        SeqNo = sockcli.generate_SeqNo()

        res = {"status": response.status, "result": {"message": '', "fare_number": job_number, "fare_type": fare_type}}

        try:   
        
            its_evt = None                               
            dic={}
            if fare_type in [ "immediate", "future"] :
                stored_fare = fare_container(fare_type)
                if not  stored_fare.error:
                     stored_fare. read_record( int(job_number ))
                if not stored_fare.error:
                    dic["zone"] = stored_fare.pickup_zone
                    dic["taxi"] = stored_fare.fi_taxi

            if fare_type == "future":  
                its_evt = future_cancel_event( int(job_number) )
                dest = msgconf.TIMEMGR
                mt = msgconf. MT_CANCEL_TIME                                      
            elif fare_type == "immediate":
                its_evt = its_event(dic)      
                its_evt.sequence_number = SeqNo
                its_evt.event_no = msgconf.EV_CNCL_CALL
                its_evt.fare = int(job_number )
                its_evt.time = int (time.time())
                dest = msgconf.DM
                mt = msgconf. MT_EVENT_MSG                
              
            response.status, resp_message, res = send_cancel_to_host(its_evt, SeqNo, dest, mt)

            if dest == msgconf.DM :
                dest = msgconf.Q_PROC
                mt =  msgconf.MT_CNCL_QENTRY
                rs,  rm, r = send_cancel_to_host(its_evt, SeqNo, dest, mt, True)

            if not resp_message:
                resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR

            if not res :
                res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type}}                 
       
            if 'result' in res:
                res['result']['job_number'] = order_dic["fare_number"][-6:].lstrip('0')
                res['result']['fare_type'] = fare_type
                res['result']['message'] = resp_message 
            else:
                res['result'] = { "message": resp_message, 'job_number':  order_dic["fare_number"][-6:].lstrip('0'), 'fare_type' :  fare_type}

            print ' res ==> ', res, ' status=',  response.status     

            res["status"] =  response.status       
                       
            sys.stdout.write("%s: returning out of handler cancel_book_order_tfc ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
            return response.status, resp_message, res

        except Exception as e:          
            sys.stdout.write("%s: *** Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            response.headers["Content-type"] = "application/json"
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    except Exception as e:
        sys.stdout.write("%s: *** Exception 2 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res




def send_cancel_to_host(its_evt, SeqNo, dest, mt, nowait=False):
    try:
       
      
        response.status = 200
        resp_message = "success"
        res = {}

        try:
            
            #print its_evt
            packed_data, size_data, errmsg = its_evt.object_to_bin()
            
            #print ' size data ==> %d  errmsg=%s'  % ( size_data, errmsg )           

        except Exception as e:
            print "send_cancel_to_host 1: Exception", str(e)
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        

        if errmsg == None and size_data > 0:
            base_fmt = 'I I I I I B B B B'                   

            print ' size data ==> %d '  % ( size_data )

            ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )   

            cabmsg.gmsg_send(packed_data, size_data, dest , 0, mt , ss_data, msgconf.CWEBS)

            sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 

            if nowait is True:
                return 200, "success", {}          

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
                            #print 'Received response  msgconf.MT_ENTER_CALL ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
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
                            #print 'Received response  msgconf.MT_MODFAREINFO ==> ', m, ' sleep_counter = ' , sleep_counter   
                            
                            job_number = str(m[9]) 
                            zone = m[11]                          
                            fare_type = "immediate"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                        
                            status =0                            
                            break;

                        elif m[3] == msgconf.MT_NEWFARE and m[13] == SeqNo:
                            #print 'Received response  msgconf.MT_NEWFARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break;


                        ### ???? ####
                        elif m[3] == msgconf.MT_UPD_FARE and m[13] == SeqNo: 
                            #print 'Received response  msgconf.MT_UPD_FARE ==> ', m, ' sleep_counter = ' , sleep_counter   
                            job_number = str (m[9]) 
                            fare_type = "future"
                            response.status = 200
                            resp_message = 'success'
                            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type,"zone": zone}}                                                    
                            status =0                            
                            break

                        elif m[3] == msgconf.MT_OP_ERR and len(m) > 12 and  m[12] == SeqNo :   
                            #print 'Received response  ### msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter   
                            if m[10] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[13]
                            response.status = 500 
                            status =0
                            break
                        
                        elif m[3] == msgconf.MT_OP_ERR and len(m) > 12 and  m[12] == 0 :   
                            #print 'Received response  &&& msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter , ' error=', m[9]  
                            resp_message = m[9]
                            response.status = 500 
                            status =0
                            break


                        elif m[3] == msgconf.MT_OP_ERR and len (m ) >=  10 :   
                            #print 'Received response  *** msgconf.MT_OP_ERR ==> ', m, ' sleep_counter = ' , sleep_counter  , ' error=', m[9]   
                            if m[9] == ErrorMsg.TFC_ZONE_ERRNO:
                                resp_message = ErrorMsg.ERROR_MSG_TFC_ZONE_ERRNO
                            else:
                                resp_message = m[9]
                            response.status = 500 
                            status =0
                            break
                      
                    else:
                        #sys.stdout.write("%s:  No response from %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
                        if status < 0:                    
                            gevent.sleep(msgconf.Q_TIMESLOT)
                      
                
              
            except Exception as e:
                sys.stdout.write("%s: send_cancel_to_host 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

        else:
            sys.stdout.write("%s: *** Could not send message to %d queue ***\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
            resp_message =  errmsg

        return response.status, resp_message, res
    except Exception as e:
        sys.stdout.write("%s: send_cancel_to_host 3 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

