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


def _dispatch_cancel_book_order(sockcli, data_src_repo):    
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__) )
        sys.stdout.write("%s: %s environment %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ) )

        
        response =  Utils.prepare_header('dispatch_cancel_book_order', "default")
        if  response.status == 401:
            return            
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            cancel_order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(cancel_order_dic) ) )
        except Exception as e:
            print 'Exception ', str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)

        try:
            fare_num = cancel_order_dic["fare_number"]
            if len (str(fare_num)) >  6:
                fare_num  = fare_num[-6:].lstrip('0')               
          
            #fare_num = int(cancel_order_dic["fare_number"])
            sys.stdout.write("%s: canceling fare number %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), cancel_order_dic["fare_number"] ))
        except Exception as e:
            #print 'invalid fare number ', cancel_order_dic["fare_number"]
            sys.stdout.write("%s: invalid fare number\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)


        itaxmsgid=''
        if cancel_order_dic.has_key("fare_type") and Config.EnableCancelByFareType:
            if cancel_order_dic["fare_type"]  == "immediate":
                itaxmsgid = "03"             
            elif cancel_order_dic["fare_type"]  == "future":
                itaxmsgid = "04"             

            if itaxmsgid != '':
                job_num = str(fare_num).ljust(6,' ')
                SeqNo = sockcli.generate_SeqNo()
                message = itaxmsgid + '0016' + job_num + SeqNo
                sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
                
                sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

                sockcli.send_client_request(message)
                resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                sleep_counter = 0

                fare_type = cancel_order_dic["fare_type"]
                res = {"status": response.status, "result": {"message": message, "fare_number": fare_num, "fare_type": fare_type}}

                while resp == '':
                    time.sleep(1)
                    resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                    sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                    sleep_counter = sleep_counter + 1
                    if sleep_counter > Config.SocketTimeoutDic["default"]:
                        break

                res = {"status": response.status, "result": {"message": '', "fare_number": fare_num, "fare_type": fare_type}}
                if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                    response.status = 200
                    res['status'] = response.status
                    res['result']['message'] = "success"                 
                else:
                    response.status = 500
                    rsp_msg = ErrorMsg.ERROR_MSG_GENERAL_ERROR                    
                    response.status, rsp_msg, res = Utils.check_error(sockcli, SeqNo, sleep_counter)


                sockcli.remove_dic_entry(SeqNo)
                Utils.set_default_headers(response)
                
                print 'response to client ', response.status, json.dumps(res)
                return json.dumps(res)

        
        for tab, itaxmsgid in zip(["farefl", "futfarefl"], ["03", "04"]):
            if itaxmsgid == "03":
                fare_num_str = str(fare_num).rjust(7,'0')
                sign_str = "-"
            if itaxmsgid == "04":
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
            except Exception as e:
                res["result"] = {"message": ErrorMsg.ERROR_MSG_CABMATEREPO + ": " + Config.DB_HOST_REPO}
                return json.dumps(res)

            for (Remark4, SequenceNumber, FareNumber) in info:
                print 'Remark4=', Remark4, 'SequenceNumber=', SequenceNumber, 'FareNumber=', FareNumber
                job_num = str(FareNumber)[-6:].lstrip('0').ljust(6,' ')
                print 'job_num=', job_num
                SeqNo =  sockcli.generate_SeqNo()
                message = itaxmsgid + '0016' + job_num + SeqNo
                sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
               
                sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

                sockcli.send_client_request(message)
                resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                sleep_counter = 0
               

                fare_type = "immediate" if itaxmsgid == '03'else "future"
               
                while resp == '':
                    time.sleep(1)
                    resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                    sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                    sleep_counter = sleep_counter + 1
                    if sleep_counter > Config.SocketTimeoutDic["default"]:
                        break

                res = {"status": response.status, "result": {"message": '', "fare_number": fare_num, "fare_type": fare_type}}
                if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                    response.status = 200
                    res['status'] = response.status
                    res['result']['message'] = "success"                 
                else:
                    response.status = 500
                    res['status']  = response.status
                    res['result']['message']  = ErrorMsg.ERROR_MSG_GENERAL_ERROR                    
                    response.status, rsp_msg, res = Utils.check_error( sockcli, SeqNo, sleep_counter)

            	sockcli.remove_dic_entry(SeqNo)

                Utils.set_default_headers(response)
                
                print 'response to client ', json.dumps(res)
                return json.dumps(res)
                
               
        res["result"] = {"message": "fare is not found in CabmateRepo DB"}
        return json.dumps(res)
    except Exception as e:
        print 'Exception ', str(e)
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)


def _dispatch_save_book_order(sockcli):
    try:
        response = Utils.prepare_header('dispatch_save_book_order', "default")
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
            print 'Exception: ', str(e)

            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
    
        if not Utils.is_flat_fare(save_order_dic):
            sys.stdout.write("%s: returning 500 because the flat fare is not set \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )                
            response.status = 500
            res["result"] =  {"job_number": -1, "zone": -1}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_FLAT_RATE_NOT_SET, res)
             

        sys.stdout.write("%s: reading pickup datetime\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
        
        lWillCall = False
        if save_order_dic.has_key("will_call"):
            if save_order_dic["will_call"] == 'Y':
                lWillCall = True

        if save_order_dic.has_key("pickup_datetime"):
            try:
                pickup_datetime = datetime.datetime.strptime(
                    save_order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                )
            except Exception as e:
                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))

        out_fare_type = {"01": "immediate", "02": "future", "1I": "immediate", "1J": "future"}
        if not lWillCall and save_order_dic.has_key("pickup_datetime"):
            try:
                sys.stdout.write("%s: save_order_dic['pickup_datetime']=%s\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                save_order_dic["pickup_datetime"]) 
                ) 
                pickup_datetime = datetime.datetime.strptime(
                    save_order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                )
            except Exception as e:
                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))

                #sys.stdout.write("%s: returning 500 because can not parse pickup_datetime\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
               
                #res["result"] =  {"job_number": -1, "fare_type": "", "zone": -1}
                #return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_PICKUP_DATETIME, res)
                #return json.dumps({"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_INVALID_PICKUP_DATETIME, "job_number": -1, "fare_type": "", "zone": zone_info["zone"]} })

            sys.stdout.write("%s: pickup datetime is determined as %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(pickup_datetime))) 

        zone_info = {}
        if "force_zone" not in save_order_dic or ("force_zone" in save_order_dic  and save_order_dic["force_zone"] != 'Y'):
            response.status, zone_info, res = Utils.check_zone(sockcli,save_order_dic)
            if response.status == 500:
                Utils.set_default_headers(response)            
                return json.dumps(res)
        elif "force_zone" in save_order_dic  and save_order_dic["force_zone"] == 'Y' and 'zone' in save_order_dic:    
            zone_info['zone'] = save_order_dic["zone"]          
        else:
            response.status = 500
            res = {"status": response.status, "result": {"message": 'Could not determine zone info'}}
            return json.dumps(res)

        try:
            if not lWillCall  and  pickup_datetime <= Utils.get_server_pickup_time(zone_info):
                if Config.lNewFareData:
                    itaxmsgid = '1I'
                else:
                    itaxmsgid = '01'
            else: 
                if lWillCall  or  pickup_datetime > Utils.get_server_pickup_time(zone_info):
                    if Config.lNewFareData:
                        itaxmsgid = '1J'
                    else:
                        itaxmsgid = '02'
        except Exception as e:
            itaxmsgid = '01'
            pass
        
        if lWillCall and save_order_dic.has_key("pickup_datetime") and save_order_dic.has_key("will_call_expiry_date"):
            save_order_dic['pickup_datetime']=''
            sys.stdout.write(" resetting pickup_datetime %s \n" % ( save_order_dic['pickup_datetime']) ) 

        sys.stdout.write("%s: fare type %s is determined\n" % (
               datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), out_fare_type[itaxmsgid]))

        SeqNo = sockcli.generate_SeqNo()
       
        try:
            new_fare = itcli.Fare(save_order_dic, zone_info["zone"], SeqNo)
            sys.stdout.write("%s: new fare is created with zone %s SeqNo %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  zone_info["zone"], SeqNo) ) 
            sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})
            msg = new_fare.to_msg()
        except Exception as e:
            sys.stdout.write("%s: save_book_order Exception *** [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)


        if len(msg) != 1512:
            sys.stdout.write("%s: invalid message length (%d) message is NOT sent to server\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), len(msg) ))   
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)

        clen = format_field.format_field(str(len(msg)), 4, True);
        message = itaxmsgid + clen + msg
        #print 'sending ', message
        sockcli.send_client_request(message)
        sys.stdout.write("%s: message is sent to a socket\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) )) 
    
        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

        sleep_counter = 0
        while resp == '' or sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
        #while resp == '' or sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] in ['90', '99'] and err_counter < 3:
            sys.stdout.write("%s: sleeping...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )    
            time.sleep(1.0)
            sys.stdout.write("%s: back from sleep...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )         
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            #print '!!!waiting for resp=', resp
            sleep_counter = sleep_counter + 1
            if sleep_counter > Config.SocketTimeoutDic["default"]:
                break
    
        sys.stdout.write("%s: final response=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )      
        
        sys.stdout.write("%s: sockcli.ITaxiSrvReqDic[%s]['msg_type']=%s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        SeqNo, 
        sockcli.ITaxiSrvReqDic[SeqNo]['msg_type']
        ))

        fare_type = ''
        if itaxmsgid == '01' or itaxmsgid == '1I':
            fare_type = 'immediate'
        elif itaxmsgid == '02' or itaxmsgid == '1J':
            fare_type = 'future' 
        try:
            fare_type = out_fare_type[itaxmsgid]
        except Exception as e:
            fare_type = 'immediate'
       


        job_number = -1
        response.status = 500
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type, "zone": zone_info["zone"]}}
        response.status, resp_message, res = Utils.check_error(sockcli,SeqNo, sleep_counter, res)
       

        sockcli.remove_dic_entry(SeqNo)

        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type, "zone": zone_info["zone"]}}            
        sys.stdout.write("%s: returning out of handler save_book_order ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
        

        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        print "dispatch save_book_order: Exception", str(e)
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)
       


def _dispatch_modify_book_order(sockcli, data_src_repo):
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response =  Utils.prepare_header('_dispatch_modify_book_order', "default")
        if response.status == 401:
            return
        #print str(request)
        #print str(request.body)
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            save_order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
            __name__, 
            str(save_order_dic) ))
        except Exception as e:
            print 'Exception: ', str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)

        #print 'save_order_dic ', save_order_dic
        #####################################################
        # check if fare exists - fare_number[-6:].lstrip('0')
        #####################################################
        if not save_order_dic.has_key("fare_number"):
            sys.stdout.write("%s: returning 500 because fare_number is invalid\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
            res["result"] =  {"message": resp_message, "job_number": -1, "fare_number": "", "zone": -1}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, res)
            
                             
        else:
            try:
                fare_num = int(save_order_dic["fare_number"])
            except Exception as e:
                sys.stdout.write("%s: returning 500 because fare_number is invalid\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
    
                res["result"] =  {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, 
                                              "job_number": -1, 
                                              "fare_number": save_order_dic["fare_number"], 
                                              "zone": -1}
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_JOB_NUM, res)

        if not Utils.is_flat_fare(save_order_dic):
            sys.stdout.write("%s: returning 500 because the flat fare is not set \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )                
            response.status = 500
            res["result"] =  {"job_number": -1, "zone": -1}
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_FLAT_RATE_NOT_SET, res)               

        try:
            lim_fare, lfu_fare, queprio = dblayer.get_fare_number(data_src_repo, save_order_dic["fare_number"])
        except Exception as e:
            lim_fare, lfu_fare, queprio = False, False, 0

        itaxmsgid = '08'
        if lim_fare == True and lfu_fare == False:
            itaxmsgid = '08'
        elif lim_fare == False and lfu_fare == True:
            itaxmsgid = '09'

        if Config.lNewFareData:
            if itaxmsgid == '08':
                itaxmsgid = '1K'
            elif itaxmsgid == '09':
                itaxmsgid = '1L'
  
        #######################################
        SeqNo = sockcli.generate_SeqNo()

        if lim_fare or lfu_fare :
            #print ' Got que prio ', queprio
            if (save_order_dic.has_key("dispatch_priority") and  save_order_dic["dispatch_priority"] == "") or  "dispatch_priority" not in  save_order_dic:
                save_order_dic["dispatch_priority"] = queprio
        	print ' que prio in db=%d dico=%s' % ( queprio, save_order_dic["dispatch_priority"])
      
        if lim_fare or lfu_fare :
            #print ' Got que prio ', queprio
            if (save_order_dic.has_key("dispatch_priority") and  save_order_dic["dispatch_priority"] == "") or  "dispatch_priority" not in  save_order_dic:
                save_order_dic["dispatch_priority"] = queprio
        #print ' que prio in db=%d dico=%s' % ( queprio, save_order_dic["dispatch_priority"])

        zone_info = {}
        response.status, zone_info, res = Utils.check_zone(sockcli,save_order_dic)
        if response.status == 500:
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_CANNOT_ZONE, res)

        lWillCall = False
        if save_order_dic.has_key("will_call"):
            if save_order_dic["will_call"] == 'Y':
                lWillCall = True

        if save_order_dic.has_key("pickup_datetime"):
            try:
                pickup_datetime = datetime.datetime.strptime(
                save_order_dic["pickup_datetime"], 
                    Config.DateFormat_SaveOrder_Input
                )
            except Exception as e:
                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))

        out_fare_type = {"08": "immediate", "09": "future", "1K": "immediate", "1L": "future"}
        if not lWillCall and save_order_dic.has_key("pickup_datetime"):
            try:
                sys.stdout.write("%s: reading pickup datetime\n" % (
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT))) 
        
                print 'save_order_dic["pickup_datetime"] ', save_order_dic["pickup_datetime"]
                sys.stdout.write("%s: save_order_dic['pickup_datetime']=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                save_order_dic["pickup_datetime"]) ) 
                pickup_datetime = datetime.datetime.strptime(save_order_dic["pickup_datetime"], Config.DateFormat_SaveOrder_Input)
            except Exception as e:
                #sys.stdout.write("%s: returning 500 because can not parse pickup_datetime\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
   
                #res ["result"] = {"job_number": -1, "fare_type": "", "zone": zone_info["zone"]}
                #return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_INVALID_PICKUP_DATETIME, res)

                pickup_datetime = Utils.get_default_server_time()
                sys.stdout.write("default time %s \n" % (pickup_datetime))
                pass    
                
        else:
            pickup_datetime = Utils.get_default_server_time()
            sys.stdout.write("default time %s \n" % (pickup_datetime))
                            
              
        try:
            itaxmsgid_new = "08"
            if not lWillCall  and  pickup_datetime <= Utils.get_server_pickup_time(zone_info):
                itaxmsgid_new = '08'
            else:
                if lWillCall  or  pickup_datetime > Utils.get_server_pickup_time(zone_info):
                    itaxmsgid_new = '09'
        except Exception as e:
            itaxmsgid_new = '08'
            pass

        if Config.lNewFareData:
            if itaxmsgid_new == '08':
                itaxmsgid_new = '1K'
            elif itaxmsgid_new == '09':
                itaxmsgid_new = '1L'

        sys.stdout.write("%s: will call\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) )
        
        sys.stdout.write("%s: pickup datetime in mod fare is determined as %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        str(pickup_datetime))) 
        sys.stdout.write("%s: fare type in mod %s is determined\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), out_fare_type[itaxmsgid_new]))
        sys.stdout.write('itaxmsg %s, itaxmsg_new %s \n' % (itaxmsgid, itaxmsgid_new))
        if not lim_fare and not lfu_fare:
            itaxmsgid = itaxmsgid_new           

        if lWillCall and save_order_dic.has_key("pickup_datetime") and save_order_dic.has_key("will_call_expiry_date"):
            save_order_dic['pickup_datetime']=''
            sys.stdout.write(" resetting pickup_datetime %s \n" % ( save_order_dic['pickup_datetime']) ) 

        sys.stdout.write("%s: modifying an existing fare %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        save_order_dic["fare_number"])
        ) 

        try:
            new_fare = itcli.Fare(save_order_dic, zone_info["zone"], SeqNo, save_order_dic["fare_number"][-6:].lstrip('0'))
            sys.stdout.write("%s: fare is modified\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), 
                Config.LOG_DATETIME_FORMAT))
            )
        except Exception as e:          
            sys.stdout.write("%s: Exception Could not create Fare object " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            Utils.set_default_headers(response)
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return json.dumps(res)
 

      	sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

        msg = new_fare.to_msg()
        clen = format_field.format_field(str(len(msg)), 4, True);
        message = itaxmsgid + clen + msg
        #print 'sending ', message
        sockcli.send_client_request(message)
        sys.stdout.write("%s: message is sent to a socket\n" % ( 
           datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT))
        ) 
    
        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

        sleep_counter = 0
        while resp == '' :
            sys.stdout.write("%s: sleeping...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )    
            time.sleep(1.0)
            sys.stdout.write("%s: back from sleep...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )         
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] in [ '90', '99']:
		break;
            #print '!!!waiting for resp=', resp
            sleep_counter = sleep_counter + 1
            if sleep_counter > Config.SocketTimeoutDic["default"]:
                break

        sys.stdout.write("%s: final response=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )      
        
        sys.stdout.write("%s: sockcli.ITaxiSrvReqDic[%s]['msg_type']=%s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
        SeqNo, 
        sockcli.ITaxiSrvReqDic[SeqNo]['msg_type']))

        #TODO
        try:
            response.status,  resp_message, res = Utils.check_error(sockcli,SeqNo, sleep_counter)
               
        except Exception as e:                
            print "Exception Could not parse response", str(e)
            Utils.set_default_headers(response)
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return json.dumps(res)

        fare_type = ''
        if itaxmsgid == '08' or itaxmsgid == '1K':
            fare_type = 'immediate'
        elif itaxmsgid == '09'or itaxmsgid == '1L':
            fare_type = 'future' 
       
        if 'result' in res:
            res['result']['job_number'] = save_order_dic["fare_number"][-6:].lstrip('0')
            res['result']['fare_type'] = fare_type
        else:
            res['result'] = { "message": resp_message, 'job_number':  save_order_dic["fare_number"][-6:].lstrip('0'), 'fare_type' :  fare_type}

        res["status"] =  response.status

        sockcli.remove_dic_entry(SeqNo)

        Utils.set_default_headers(response)
       
             
        if not res:
            resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type, "zone": zone_info["zone"]}}            

        sys.stdout.write("%s: returning out of handler modify_book_order ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
        return Utils.make_error_response(response, response.status, resp_message, res)
 
    except Exception as e:
        sys.stdout.write("%s: dispatch modify_book_order: Exception" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e) ) )
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_GENERAL_ERROR)



def _request_fare_details(sockcli):
    try:
        response =  Utils.prepare_header('request_fare_details', "default")
        if response.status == 401:
            return

    except Exception as e:
        print "Exception %s" % (str(e))
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)

    try:
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        clen = request.content_length
        request.body.seek(0)

        msg_dic = json.loads(str(request.body.read(clen)))
        itaxmsgid = "53" # default
        if Config.lNewFareData:
            itaxmsgid = "0C" # default
        sys.stdout.write("%s: msg_dic %s\n" % (
               datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
               str(msg_dic) ))
        if msg_dic.has_key("fare_number"):
            fare_num = msg_dic["fare_number"][-6:].ljust(6, ' ')
        else:
            return
        if msg_dic.has_key("fare_type"):
            if msg_dic["fare_type"]  == "future":
                itaxmsgid = "55"
            if Config.lNewFareData:
                     itaxmsgid = "0E" # default
            if msg_dic["fare_type"]  == "run":
                itaxmsgid = "58"
            if Config.lNewFareData:
                     itaxmsgid = "0G" # default
        sys.stdout.write("%s: request fare details fare number %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg_dic["fare_number"] ))
        
        job_num = str(fare_num)
        SeqNo = sockcli.generate_SeqNo()
        tmpSeq = 10*'0'
        #mymsg  = job_num + SeqNo + tmpSeq
        mymsg  = job_num + SeqNo + SeqNo
        myclen = format_field.format_field(str(len(mymsg)), 4, True)
        message = itaxmsgid + '0026' + mymsg 
        sys.stdout.write("%s: sending to a socket message [%s]\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
        sockcli. init_dic_entry( SeqNo, {'msg': '', 'msg_type': ''} )

        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
        sleep_counter = 0
        while resp == '' :
            time.sleep(1)
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            sleep_counter = sleep_counter + 1
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                sockcli.remove_dic_entry(SeqNo)
                sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

            if sleep_counter > Config.SocketTimeoutDic["default"]:
                 message = ErrorMsg.ERROR_MSG_SOCKET_TIMEOUT
                 break
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '99':
                 message = ErrorMsg.ERROR_MSG_NACK
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] in ['54', '56', '59', '0D', '0F', '0H']:
                Utils.set_default_headers(response)
                response.status  = 200
                message = "success"
                res = {'status': response.status, 'result': {'message': message }}
                res["local_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1434:1435]
                res["bid_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1502:1503]
                res["priority_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1501:1502]
                res["restricted_code"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1503:1504]
                res["no_service"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1504:1505]
                res["pick_up_building_type"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1509:1510]
                res["dest_building_type"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1510:1511]
                if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] in ['0D', '0F', '0H']:
                    res["local_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1434:1435]
                    res["bid_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1831:1832]
                    res["priority_call"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1830:1831]
                    res["restricted_code"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1832:1833]
                    res["no_service"] = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][1833:1834]
                    bid_info=[]
                    start_idx=1834
                    len_item=33
                    for i in range(0,4):
                        bid = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][start_idx:start_idx+len_item]
                        start_idx += len_item
                        bid_info.append(bid)
                        '''
                        for i in bid_info:
                            print ' bid ->' , i
                        '''
                        res["bid_info"] = bid_info
                break

        sockcli.remove_dic_entry(SeqNo)        

        #print 'response to client ', json.dumps(res)
        return json.dumps(res)
    except Exception as e:
        print "Exception %s" % (str(e))
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)


#TEST ONLY for now ...
def _dispatch_cancel_book_order_fast(sockcli, data_src_repo):    
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__) )
        sys.stdout.write("%s: %s environment %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ) )

        
        response =  Utils.prepare_header('dispatch_cancel_book_order', "default")
        if  response.status == 401:
            return            
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)
        try:
            cancel_order_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(cancel_order_dic) ) )
        except Exception as e:
            print 'Exception ', str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)

        try:
            fare_num = cancel_order_dic["fare_number"]
            if len (str(fare_num)) >  6:
                fare_num  = fare_num[-6:].lstrip('0')               
          
            #fare_num = int(cancel_order_dic["fare_number"])
            sys.stdout.write("%s: canceling fare number %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), cancel_order_dic["fare_number"] ))
        except Exception as e:
            #print 'invalid fare number ', cancel_order_dic["fare_number"]
            sys.stdout.write("%s: invalid fare number\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)


        itaxmsgid=''
        if cancel_order_dic.has_key("fare_type") and Config.EnableCancelByFareType:
            if cancel_order_dic["fare_type"]  == "immediate":
                itaxmsgid = "03"             
            elif cancel_order_dic["fare_type"]  == "future":
                itaxmsgid = "04"             

            if itaxmsgid != '':
                job_num = str(fare_num).ljust(6,' ')
                SeqNo = sockcli.generate_SeqNo()
                message = itaxmsgid + '0016' + job_num + SeqNo
                sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
                
                sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

                sockcli.send_client_request(message)
                resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                sleep_counter = 0

                fare_type = cancel_order_dic["fare_type"]
                res = {"status": response.status, "result": {"message": message, "fare_number": fare_num, "fare_type": fare_type}}

                while resp == '':
                    time.sleep(1)
                    resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                    sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                    sleep_counter = sleep_counter + 1
                    if sleep_counter > Config.SocketTimeoutDic["default"]:
                        break

                res = {"status": response.status, "result": {"message": '', "fare_number": fare_num, "fare_type": fare_type}}
                if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                    response.status = 200
                    res['status'] = response.status
                    res['result']['message'] = "success"                 
                else:
                    response.status = 500
                    rsp_msg = ErrorMsg.ERROR_MSG_GENERAL_ERROR                    
                    response.status, rsp_msg, res = Utils.check_error(sockcli, SeqNo, sleep_counter)


                sockcli.remove_dic_entry(SeqNo)
                Utils.set_default_headers(response)
                
                print 'response to client ', response.status, json.dumps(res)
                return json.dumps(res)

        
        for itaxmsgid in ("03", "04"):      
            job_num = fare_num_str # str(FareNumber)[-6:].lstrip('0').ljust(6,' ')
            print 'job_num=', job_num
            SeqNo =  sockcli.generate_SeqNo()
            message = itaxmsgid + '0016' + job_num + SeqNo
            sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
               
            sockcli.init_dic_entry(SeqNo, {'msg': '', 'msg_type': ''})

            sockcli.send_client_request(message)
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sleep_counter = 0
               

            fare_type = "immediate" if itaxmsgid == '03'else "future"
               
            while resp == '':
                time.sleep(1)
                resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
                sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                sleep_counter = sleep_counter + 1
                if sleep_counter > Config.SocketTimeoutDic["default"]:
                    break

            res = {"status": response.status, "result": {"message": '', "fare_number": fare_num, "fare_type": fare_type}}
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
                response.status = 200
                res['status'] = response.status
                res['result']['message'] = "success"                 
            else:
                response.status = 500
                rsp_msg = ErrorMsg.ERROR_MSG_GENERAL_ERROR                    
                response.status, rsp_msg, res = Utils.check_error( sockcli, SeqNo, sleep_counter)

            sockcli.remove_dic_entry(SeqNo)

            Utils.set_default_headers(response)
                
            print 'response to client ', json.dumps(res)
            return json.dumps(res)               
               
        return json.dumps(res)
    except Exception as e:
        print 'Exception ', str(e)
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)



def _update_payment_type(sockcli, data_src_repo): 

    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: update_payment_type %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))
       
        response =  Utils.prepare_header('update_payment_type', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        try:
            update_payment_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: update_payment_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(update_payment_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)

        ChargeTypeID = str(update_payment_dic["ChargeTypeID"])
        if Config.PaymentTypeDic.has_key(ChargeTypeID):
            payment_type = Config.PaymentTypeDic[ChargeTypeID]
        else:
            payment_type = "OT"
        try:
            j = update_payment_dic["job_num"]
            job_num = int(str(j))
            job =  format_field.format_field(j, 6, True)
        except Exception as e:
            job = 6*' '
            res['result'] = {'message': 'invalid job num'}
            return json.dumps(res)
        # constructing envelop
        SeqNo = sockcli.generate_SeqNo()
        # messageid
        itaxmsgid = '1E0032'

        message = itaxmsgid + SeqNo + job + payment_type + format_field.format_field(' ', 14, True)
        sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
        sockcli.lock.acquire()
        sockcli.ITaxiSrvReqDic[SeqNo] = {'msg': '', 'msg_type': ''}
        sockcli.lock.release()
        sockcli.send_client_request(message)
        sys.stdout.write("%s: message is being sent to a socket\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )

        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

        sleep_counter = 0
        while resp == '':
            sys.stdout.write("%s: sleeping...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            time.sleep(1)
            sys.stdout.write("%s: back from sleep...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            sleep_counter = sleep_counter + 1
            if sleep_counter > 10:
                break
        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
            sockcli.remove_dic_entry(SeqNo)  
            response.status = 200
            res = {'status': response.status, 'result': {'message': 'success'}}
            return json.dumps(res)
        else:
            sockcli.remove_dic_entry(SeqNo)

            res['result'] = {'message': 'socket timeout'}
            return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: update_payment_type terminated due to exception\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "update_payment_type: Exception %s" %  (str(e))
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)


def _update_fare_amount(sockcli, data_src_repo):
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: %s environment %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ))
   
        response =  Utils.prepare_header('update_fare_amount', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}

        try:
            update_fare_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: update_fare_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(update_fare_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)  

        try:
            fare_am = int(str(update_fare_dic["flat_rate"]))
            #fare_amount = format_field.format_field(("%2.2f" % (fare_am / 100.0)), 8, True);
            fare_amount = format_field.format_field(str(fare_am), 8, True);
        except Exception as e:
            fare_amount = 8*' '
            res['result'] = {'message': 'invalid fare amount'}
            return json.dumps(res)
        try:
            j = update_fare_dic["fare_number"][-6:].lstrip('0')
            job_num = int(str(j))
            job =  format_field.format_field(j, 6, True)
        except Exception as e:
            job = 6*' '
            res['result'] = {'message': 'invalid job num'}
            return json.dumps(res)

        # constructing envelop
        SeqNo = sockcli.generate_SeqNo()
        # messageid
        itaxmsgid = '1F0032'
        spare = 8*' '
        message = itaxmsgid + SeqNo + job + fare_amount + spare
        sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
        sockcli.lock.acquire()
        sockcli.ITaxiSrvReqDic[SeqNo] = {'msg': '', 'msg_type': ''}
        sockcli.lock.release()
        sockcli.send_client_request(message)
        sys.stdout.write("%s: message is being sent to a socket\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )

        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

        sleep_counter = 0
        while resp == '':
            sys.stdout.write("%s: sleeping...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            time.sleep(1)
            sys.stdout.write("%s: back from sleep...\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            sleep_counter = sleep_counter + 1
            if sleep_counter > 10:
                break
        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
            sockcli.remove_dic_entry(SeqNo)
            response.status = 200
            res = {'status': response.status, 'result': {'message': 'OK'}}
            return json.dumps(res)
        else:
            sockcli.remove_dic_entry(SeqNo)  
            res['result'] = {'message': 'socket timeout'}
            return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: exception in update_fare_amount\n" % ( datetime.datetime.strftime(datetime.datetime.now(), 
            Config.LOG_DATETIME_FORMAT) ))
        print "update_fare_amount: Exception ", str(e)
        Utils.set_default_headers(response)
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)



def _update_destination(sockcli, data_src_repo):    
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: %s environment %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, str(request.environ) ))
        
        response =  Utils.prepare_header('update_destination', "default")
        if  response.status == 401:
            return            


        clen = request.content_length
        request.body.seek(0)
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        try:
            update_addr_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(update_addr_dic) ))
        except Exception as e:
            print "Exception ", str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)  
        try:
            if not update_addr_dic["fare_type"] == "immediate":
                res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_FARE_TYPE}
                return json.dumps(res)
        except Exception as e:
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_FARE_TYPE}
            return json.dumps(res)
        try:
            job_num = int(update_addr_dic["fare_number"].lstrip('0'))     
        except Exception as e:
            res["result"] = {'message': ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)
        msg_dic = {"fare_number": str(job_num)}
        for akey in ["dest_street_number", 
                     "dest_street_name", 
                     "dest_street_type", 
                     "dest_apartment",
                     "dest_building_name", 
                     "dest_city_name",
                     "dest_zip", 
                     "dest_postalcode"]:
            try:
                res = format_field.str_field(update_addr_dic[akey])
                msg_dic[akey] = res 
            except Exception as e:
                pass
        #GPS x / y   : -75915000 / 45341000
        for gpskey in ["dest_latitude", "dest_longitude"]:
            try:
                val = abs(update_addr_dic[gpskey]) 
                '''
                if val  < 0.000001 or val > 180.0 :
                    sys.stdout.write("%s: invalid gps ...\n" % val )
                    return json.dumps(res)
                if val  > 90.0  and gpskey == "dest_latitude":
                    sys.stdout.write("%s: invalid latitude ...\n" % val )
                    return json.dumps(res)
                ''' 
                if val  > 0.000001 and val <= 180.0 :
                    msg_dic[gpskey] = int(update_addr_dic[gpskey]  * 1000000)
                #msg_dic[gpskey] = str(int(update_addr_dic[gpskey]  * 1000000))
            except Exception as e:
                print 'Exception ', str(e) 
        sys.stdout.write("%s: message dictionary %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), json.dumps(msg_dic) ) )
        # constructing envelop
        SeqNo = sockcli.generate_SeqNo()
        # messageid
        itaxmsgid = "0B"
        itaxmsg = SeqNo + json.dumps(msg_dic)
        sz = len(itaxmsg)
        if sz > 1024:
            res['result'] = {"message": ErrorMsg.ERROR_MSG_INVALID_MSG_LENGTH}
            return json.dumps(res)
       
        message = itaxmsgid + str(sz).rjust(4, '0') + itaxmsg
        sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), message))
        sockcli.lock.acquire()
        sockcli.ITaxiSrvReqDic[SeqNo] = {'msg': '', 'msg_type': ''}
        sockcli.lock.release()
        sockcli.send_client_request(message)
        sys.stdout.write("%s: message is sent to a socket\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )

        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()

        sleep_counter = 0
        while resp == '':
            time.sleep(1)
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            sleep_counter = sleep_counter + 1
            if sleep_counter > Config.SocketTimeoutDic["default"]:
                break

        sys.stdout.write("%s: FINAL response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )

        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':

            sockcli.remove_dic_entry(SeqNo)

            response.status = 200
            res = {"status": response.status, "result": {"message": "success"}}
            return json.dumps(res)
        else:
            try:
                response.status, errmsg, res = Utils.check_error(sockcli,SeqNo, sleep_counter)
               
            except Exception as e:
                print "Exception ", str(e)
                print "Could not parse response"
                Utils.set_default_headers(response)
                response.status = 500
                res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
                return json.dumps(res)

        sockcli.remove_dic_entry(SeqNo)

        return json.dumps(res)
    except Exception as e:
        print "Exception ", str(e)
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)

