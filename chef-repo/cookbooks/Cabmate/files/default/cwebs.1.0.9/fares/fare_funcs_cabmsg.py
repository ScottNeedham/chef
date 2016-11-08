# coding=utf-8
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import gevent 
import datetime
import json
import sys
import time
import struct

import socketcli
import cabmsg
import format_field
import itcli
import msgconf

import config.cwebsconf as Config

import server_utils as Utils
import errormsg as ErrorMsg

from msg_containers.payment_container import payment_container
from msg_containers.fare_container import  fare_container

def _update_payment_type(sockcli, data_src_repo): 

    try:       
        sys.stdout.write("%s: update_payment_type %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))
       
        response =  Utils.prepare_header('update_payment_type', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        res = {'status': response.status, 'result': {'message': 'failure'}}
        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)

        ChargeTypeID = str(dic["ChargeTypeID"])
        if Config.PaymentTypeDic.has_key(ChargeTypeID):
            payment_type = Config.PaymentTypeDic[ChargeTypeID]
        else:
            payment_type = "OT"

        try:        
            job_num = int(str( dic["job_num"] ))
            
        except Exception as e:
            sys.stdout.write("%s: Exception 1 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
           
            res['result'] = {'message': 'invalid job num'}
            return json.dumps(res)
        
        dic['fare'] = job_num
        dic['payment_type'] = payment_type
        try:
            SeqNo = socketcli. sClient.generate_seqno()                       
           
            #print dic
            evt = payment_container(SeqNo, dic, msgtype=msgconf.MT_PAYMENT_TYPE_CHANGE)

           #print evt

        except Exception as e:
            sys.stdout.write("%s: Exception 2 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, response.status, resp_message, res)            

        try:
            sys.stdout.write("%s: new object is created with SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  SeqNo) ) 

            response.status, resp_message, res = send_request_to_host(evt, SeqNo,  msgconf.TFC, evt.msgid, True)

            return Utils.make_error_response( response, response.status, resp_message, res)
      
        except Exception as e:
            sys.stdout.write("%s: Exception 3 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, response.status, resp_message, res)            

    except Exception as e:
        sys.stdout.write("%s: Exception 4 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
        return Utils.make_error_response(response, response.status, resp_message, res)            


           
    except Exception as e:
        sys.stdout.write("%s: update_payment_type terminated due to exception %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)


def _update_fare_amount(sockcli, data_src_repo):
    try:        
        sys.stdout.write("%s: %s environment %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ))
   
        response =  Utils.prepare_header('update_fare_amount', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        res = {'status': response.status, 'result': {'message': 'failure'}}

        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: update_fare_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)  

        try:
            fare_am = int(str(dic["flat_rate"]))          
        except Exception as e:
            sys.stdout.write("%s: Exception 1 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
           
            res['result'] = {'message': 'invalid fare amount'}
            return json.dumps(res)

        try:            
            job_num = int(str(  dic["fare_number"][-6:].lstrip('0') ))
            
        except Exception as e:
            sys.stdout.write("%s: Exception 2 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )            
           
            res['result'] = {'message': 'invalid job num'}
            return json.dumps(res)
    
        dic['fare'] = job_num
        dic['fare_amount'] = fare_am
        try:
            SeqNo = socketcli. sClient.generate_seqno()                       
           
            #print dic
            evt = payment_container(SeqNo, dic, msgtype=msgconf.MT_UPDATE_FARE_AMOUNT)

            #print evt

        except Exception as e:
            sys.stdout.write("%s: Exception 2 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, response.status, resp_message, res)            

        try:
            sys.stdout.write("%s: new object is created with SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  SeqNo) ) 

            response.status, resp_message, res = send_request_to_host(evt, SeqNo,  msgconf.TFC, evt.msgid, True)

            return Utils.make_error_response( response, response.status, resp_message, res)
      
        except Exception as e:
            sys.stdout.write("%s: Exception 3 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, response.status, resp_message, res)            

    except Exception as e:
        sys.stdout.write("%s: Exception 4 %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
        return Utils.make_error_response(response, response.status, resp_message, res)            


           
    except Exception as e:
        sys.stdout.write("%s: update_payment_type terminated due to exception %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)
      



def _update_destination(sockcli, data_src_repo):    
    try:
        
        sys.stdout.write("%s: %s environment %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ))
        
        response =  Utils.prepare_header('_update_destination', "default")
        if  response.status == 401:
            return            


        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(dic) ))
        except Exception as e:
            print "Exception ", str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)  
        
        try:
            if not dic["fare_type"] == "immediate":
                res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_FARE_TYPE}
                return json.dumps(res)
        except Exception as e:
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_FARE_TYPE}
            return json.dumps(res)
        
        try:
            fare_num = dic["fare_number"] if "fare_number" in dic else ''
            if len (str(fare_num)) >  6:
                job_num  = int (fare_num[-6:].lstrip('0') )
            else:
                job_num = int(dic["fare_number"].lstrip('0'))     
        except Exception as e:
            res["result"] = {'message': ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)
        
        msg_dic = {"fare_number": str(job_num)}

        myzip = zip (  ["dest_street_number", 
                        "dest_street_name", 
                        "dest_street_type", 
                        "dest_apartment",
                        "dest_building_name", 
                        "dest_city_name",
                        "dest_zip", 
                        "dest_postalcode",
                        "dest_latitude",
                        "dest_longitude"],

                    ["destination_street_number", 
                        "destination_street_name", 
                        "destination_street_type", 
                        "destination_apartment",
                        "destination_building_name", 
                        "destination_city_name",
                        "destination_zip", 
                        "destination_postalcode",
                        "destination_latitude",
                        "destination_longitude"]
                )

        for t in myzip:
            try:
                if  t[0] in dic:
                    if t[0] in  ["dest_latitude", "dest_longitude"]:
                        val = abs(dic[t[0]])               
                              
                        if val  > 0.000001 and val <= 180.0 :
                            msg_dic[ t[1] ] = int(val  * 1000000)
                    else:
                        res = format_field.str_field(dic[t[0]])
                        msg_dic[t[1]] = res 
            except Exception as e:
                sys.stdout.write("%s: Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))               
                
        sys.stdout.write("%s: message dictionary %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), json.dumps(msg_dic) ) )
        
        try:
            SeqNo = sockcli.generate_SeqNo()            
     
            fare_type = dic["fare_type"] if "fare_type" in dic else ''
        
            if fare_type in [ "immediate", "future"] :
                stored_fare = fare_container(fare_type)
                if not  stored_fare.error:
                     stored_fare. read_record( int(job_num ))
                if not stored_fare.error:
                    msg_dic["dest_zone"] = stored_fare.dest_zone
            
            new_fare = itcli.Fare(msg_dic, stored_fare.pickup_zone, SeqNo, job_num)   

            res = {"status": response.status, "result": {"message": '', "fare_number": job_num, "fare_type": fare_type}}      
            
            #send the fare to TFC
            response.status,  resp_message, res = send_fare_to_host(new_fare, msg_dic, SeqNo, job_num)

        except Exception as e:          
            sys.stdout.write("%s: Exception 6 Could not create Fare object %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            Utils.set_default_headers(response)
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return json.dumps(res)
 
    
       
        if 'result' in res:
            res['result']['job_number'] = msg_dic["fare_number"][-6:].lstrip('0')
            res['result']['fare_type'] = fare_type
        else:
            res['result'] = { "message": resp_message, 'job_number':  msg_dic["fare_number"][-6:].lstrip('0'), 'fare_type' :  fare_type}

        res["status"] =  response.status

     
        Utils.set_default_headers(response)
             
        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type, "zone": zone_info["zone"]}}            

        sys.stdout.write("%s: returning out of handler modify_book_order_tfc ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        sys.stdout.write("%s: dispatch modify_book_order_tfc: Exception 7 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

    except Exception as e:
        print "Exception ", str(e)
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)




def send_message_to_cabmsg(packed_data, size_data, SeqNo, dest, mt, nowait=False):
    try:
       
        response.status = 200
        resp_message = "success"
        res = {}
        scndid=0
      
        base_fmt = 'I I I I I B B B B'                   

        print ' size data ==> %d '  % ( size_data )

        ss_data = struct.Struct(base_fmt + '%ds' % ( size_data ) )   

        cabmsg.gmsg_send(packed_data, size_data, dest , scndid, mt , ss_data, msgconf.CWEBS)

        sys.stdout.write("%s: message is sent to the %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 

        if nowait is True:
            return response.status,  resp_message, res     

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
                     
            
            return response.status,  resp_message, res          
              
        except Exception as e:
            sys.stdout.write("%s:  send_message_to_cabmsg 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)


        return response.status,  resp_message, res     

    except Exception as e:
        sys.stdout.write("%s:  send_message_to_cabmsg 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
     
    return response.status,  resp_message, res     
      


def send_request_to_host(evt, SeqNo, dest, mt, nowait=False):
    try:     
        response.status = 200
        resp_message = "success"
        res = {}

        try:
            
            print evt
            packed_data, size_data, errmsg = evt.object_to_bin()
            
            print ' size data ==> %d  errmsg=%s'  % ( size_data, errmsg )           

        except Exception as e:
            print "send_request_to_host 1: Exception", str(e)
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
        

        if errmsg == None and size_data > 0:
             response.status, resp_message, res = send_message_to_cabmsg(packed_data, size_data, SeqNo, dest, mt, nowait )
        else:
            sys.stdout.write("%s: *** Could not send message to %d queue ***\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
            resp_message =  errmsg

        return response.status, resp_message, res
    except Exception as e:
        sys.stdout.write("%s: send_to_host 3 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res




def send_fare_to_host(new_fare, order_dic, SeqNo, fare_num):
    try:
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        response.status = 500
        res = {}

        try:
 
            packed_data, size_data, errmsg = new_fare.fare_to_bin()            
            dest = msgconf.TFC
            mt = msgconf. MT_MODADDRESSFARE

        except Exception as e:
            print "send_fare_to_host 1: Exception", str(e)
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
                sys.stdout.write("%s: dispatch send_fare_to_host 2 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

        sys.stdout.write("%s: Received response from  %d queue\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dest )) 
        return response.status, resp_message, res
    except Exception as e:
        sys.stdout.write("%s: send_to_host 3 : Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  str(e) ) )         
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
