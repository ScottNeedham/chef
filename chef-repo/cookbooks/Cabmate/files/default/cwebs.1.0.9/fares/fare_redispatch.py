
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

from fares.its_event import its_event

from msg_containers.fare_container import  fare_container

import msgconf

from fares.fare_cancel_tfc import send_cancel_to_host

def _redispatch_order(sockcli, data_src_repo):
    try:        
        response =  Utils.prepare_header('redispatch_order', "default")
        if  response.status == 401:
            return            
        response.status = 500
        Utils.set_default_headers(response)
        resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR

        res = {"status": response.status, "result": {"message": resp_message } }

        clen = request.content_length
        request.body.seek(0)
        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(dic) ) )
        except Exception as e:
            print 'Exception ', str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)

        try:
            fare_num = dic["fare_number"]
            if len (str(fare_num)) >  6:
                fare_num  = fare_num[-6:].lstrip('0')               
          
            sys.stdout.write("%s: redispatching fare number %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), dic["fare_number"] ))
        except Exception as e:          
            sys.stdout.write("%s: invalid fare number\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_JOB_NUM}
            return json.dumps(res)

 
        fare_type = ''
        if dic.has_key("fare_type") :
            fare_type = dic["fare_type"]                 

            if fare_type in [ "immediate", "future"] :
                fare_num = str(fare_num).ljust(6,' ')
              
            try:                    
                response.status, resp_message, res = redispatch(sockcli, fare_num, fare_type, dic, response)
                return Utils.make_error_response( response, response.status, resp_message, res)
            except Exception as e:          
                sys.stdout.write("%s: Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                Utils.set_default_headers(response)
                response.status = 500
                res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
                return json.dumps(res)
        else:        
            res["result"] = {"message": "fare cannot be re-dispatched. fare_type must be immediate."}
            return json.dumps(res)
    except Exception as e:
        print '*** Exception 2 ', str(e)
        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)  

    return json.dumps(res)



def redispatch(sockcli, old_job_number, fare_type, dic, response):
    try:
        SeqNo = sockcli.generate_SeqNo()
        job_number = -1
        res = {"status": response.status, "result": {"message": '', "fare_number": job_number, "fare_type": fare_type}}

        try:   
        
            its_evt = None                               
            dic={}
            if fare_type in [ "immediate", "future"] :
                stored_fare = fare_container(fare_type)
                if not  stored_fare.error:
                     stored_fare. read_record( int(old_job_number ))
                if not stored_fare.error:
                    dic["zone"] = stored_fare.pickup_zone
                    dic["taxi"] = stored_fare.fi_taxi                                 
            
                dest = msgconf.TFC
                its_evt = its_event(dic)      
                its_evt.sequence_number = SeqNo
                its_evt.event_no = msgconf.EV_REDISPATCH
                its_evt.fare = int(old_job_number )
                its_evt.time = int (time.time()) 
                its_evt.taxi = stored_fare.fi_taxi
                its_evt.redisp_taxi  =  stored_fare.fi_taxi       
                mt = msgconf. MT_EVENT_MSG                        
 
                response.status, resp_message, res = send_cancel_to_host(its_evt, SeqNo, dest, mt)
          
                if not resp_message:
                    resp_message = ErrorMsg.ERROR_MSG_GENERAL_ERROR

                if not res :
                    res = {"status": response.status, "result": {"message": resp_message, "job_number": job_number, "fare_type": fare_type}}                 
       
                if not 'result' in res:                                       
                    res['result'] = { "message": resp_message, 'job_number': job_number , 'fare_type' :  fare_type}

                print ' res ==> ', res, ' status=',  response.status     

                res["status"] =  response.status       
                       
                sys.stdout.write("%s: returning out of handler redispatch ... [%s] \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , json.dumps(res) ) )
       
                return response.status, resp_message, res

        except Exception as e:          
            sys.stdout.write("%s: *** Exception 1 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            Utils.set_default_headers(response)
            response.status = 500
            res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
            return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    except Exception as e:
        sys.stdout.write("%s: *** Exception 2 %s " % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        Utils.set_default_headers(response)
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return response.status,  ErrorMsg.ERROR_MSG_GENERAL_ERROR, res

    return response.status, ErrorMsg.ERROR_MSG_GENERAL_ERROR, res