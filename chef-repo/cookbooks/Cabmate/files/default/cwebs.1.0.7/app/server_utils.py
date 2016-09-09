
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort
import config.cwebsconf as Config
import secretconf
import datetime
import json
import os
import sys
import time
import copy
import readhmac
import zqqwrap 
import smalldb
import socketcli
import socket
from fares import itcli
import format_field
import dblayer
import validpr
import driver
import vehicle
import msgconf
import cabmsg
import struct
import sanity_check
import scap


import scap_funcs


import errormsg as ErrorMsg


def make_error_response(response, errno, errmsg, dic=None):
    try:
        response.status = errno
        response.headers["Content-type"] = "application/json"
        if isinstance(dic, dict):
            res = dic.copy()
        else:
            res = { 'status':'' , 'result':{'message':  ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
    

        if 'result' in res:
            res ['result']['message'] =   errmsg 
        else:
            res ['result'] = { 'message' :   errmsg  }
        

        res['status'] =  response.status
    
    except Exception as e:
        sys.stdout.write("%s: exception in make_response %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        pass

    if not res:
        res = { 'status': errno,  'result':{'message':   ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
  
    return json.dumps(res)



def check_error(sockcli, SeqNo, sleep_counter=None, dic=None):
    try:
        
        errmsg=ErrorMsg.ERROR_MSG_GENERAL_ERROR
        status=500
        res = {'status': status, 'result': {'message': errmsg}}             

        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
            status = 200
            errmsg = 'success'
            res = {'status': status, 'result': {'message': 'success'}}           
        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '99':
            status = 500
            if sockcli.ITaxiSrvReqDic[SeqNo]['msg_length'] == 132:
                errmsg =  str(sockcli.ITaxiSrvReqDic[SeqNo]['msg'][14:95] ).rstrip()
            else:
                errmsg = ErrorMsg.ERROR_MSG_NACK
            res = {"status": response.status, "result": {"message": errmsg}}
        elif sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'].strip() == '' and sleep_counter and sleep_counter == Config.SocketTimeoutDic["default"]:
            res["result"] = {"message": ErrorMsg.ERROR_MSG_SOCKET_TIMEOUT}
            status = 500
            errmsg = ErrorMsg.ERROR_MSG_GENERAL_ERROR
        elif sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] in ['50', '51', '52', '57']:
            job_number_int = int(sockcli.ITaxiSrvReqDic[SeqNo]['msg'][10:16])
            sys.stdout.write("%s:  job number int =%d\n" % ( 
                    datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                    job_number_int))
            if job_number_int > 0:
                job_number = sockcli.ITaxiSrvReqDic[SeqNo]['msg'][10:16]
                sys.stdout.write("%s: success - job number=%s\n" % (
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
                        str(job_number) ) 
                    )
                status  = 200
                errmsg  = 'success'
                if dic is None:
                    res = {"status": status, "result": {"message": errmsg, "job_number": job_number } }
                else:
                    res = {"status": status, "result": {"message": errmsg, "job_number": job_number, "zone": dic["result"]["zone"],  "fare_type": dic["result"]["fare_type"] } }

            else:
                raise Exception("invalid job number")
            status = 200
    except Exception as e:
        sys.stdout.write("%s: exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        pass

  
    return status, errmsg, res




def prepare_header(calling_fn, resource_key):
    try:
        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: prepare_header for %s :  %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            calling_fn,
            str(request.environ) ))

        header_hmac = readhmac.get_hmac_from_header(request.environ,
            secretconf.resource_secrets[resource_key])
        if not header_hmac[1] == header_hmac[2]:
            response.status = 401
            response.headers["HTTP_AUTHORIZATION"] = header_hmac[4] + ": Not Authorized"
            return response
        else:
            response.headers["HTTP_AUTHORIZATION"] = header_hmac[4] + ": Authorized"
        return response
    except Exception as e:
         print 'exception ', str(e)

    return response



def get_zstatus():
    file_name = "/data/zstatus/normstat.fl"
    zone_status_struct = struct.Struct('i i i i') # Should be 16 bytes.
    zone_status = {}
    try:
        fp = open(file_name, "r")
        fp.close()
    except Exception as e:
         print 'exception ', str(e)
         return zone_status
    with open(file_name, "rb") as f:  
        count = 0 
        while True:
            count = count + 1
            data = f.read(zone_status_struct.size)
            if count == 1:
                continue
            if not data or count > 1000:
                break
            else:
                udata = zone_status_struct.unpack(data)
                print count, udata
                if udata[0] > 0 and udata[1] >= 0 and udata[2] >= 0 and udata[3] >= 0:
                    zone_status[str(udata[0])] = [udata[1], udata[2]] 
    return zone_status            


def get_zone_by_gps(sockcli, lat, lon, fleetnum):

    try:

        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        res = {"zone": -1, "lead_time": -1}
       
        
        SeqNo = sockcli.generate_SeqNo()
        sockcli.lock.acquire()
        sockcli.ITaxiSrvReqDic[SeqNo] = {'msg': '', 'msg_type': ''}
        sockcli.lock.release()
   
        itaxmsgid = '92' 
        msg=''
        msg = SeqNo + str(fleetnum).rjust(5, '0')
        sys.stdout.write("%s: message  seqno + fleetnum (%s)  \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg))
     
        msg += str(int(lon * 1000000)).ljust(10)
        sys.stdout.write("%s: message  (%s)  \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg))
        msg += str(int(lat * 1000000)).ljust(10)
        sys.stdout.write("%s: message  (%s)  \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg))
        sys.stdout.write("%s: sending to a socket message %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), msg))

        if len(msg) != 35 :
            sys.stdout.write("%s: invalid message len (%s)  %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), clen, msg))
            return res

        message = itaxmsgid + '0035' + msg
        #
        #               163747614800001-74009153 40706202
        sockcli.send_client_request(message)
        resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
        sleep_counter = 0
        while resp == '' or sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '90':
            time.sleep(1)
            resp = sockcli.ITaxiSrvReqDic[SeqNo]['msg'].strip()
            #sys.stdout.write("%s: response=%s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
            sleep_counter = sleep_counter + 1
            if sleep_counter > Config.SocketTimeoutDic["default"]:
                sys.stdout.write("%s: response=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
                break
        sys.stdout.write("%s: final response=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), resp) )
        sys.stdout.write("%s: sockcli.ITaxiSrvReqDic[%s]=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), SeqNo, sockcli.ITaxiSrvReqDic[SeqNo]) )
        sys.stdout.write("%s: sockcli.ITaxiSrvReqDic[%s]['msg_type']=%s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
            SeqNo, 
            sockcli.ITaxiSrvReqDic[SeqNo]['msg_type']))
        if sockcli.ITaxiSrvReqDic[SeqNo]['msg_type'] == '93' or sockcli.ITaxiSrvReqDic[SeqNo]['msg_type']=='':
            try:
                #sys.stdout.write("%s: parsing zone and lead time\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )
                res["zone"] = int(sockcli.ITaxiSrvReqDic[SeqNo]['msg'][35:40])
                res["lead_time"] = int(sockcli.ITaxiSrvReqDic[SeqNo]['msg'][40:44])
                response.status  = 200
                message = "OK"
                #sys.stdout.write("%s: zone=%s lead time=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), zone_info["zone"], zone_info["lead_time"]))                
            except Exception as e:
                response.status = 500 
                message = ErrorMsg.ERROR_MSG_CANNOT_ZONE                
        else:
            response.status = 500
            message = ErrorMsg.ERROR_MSG_GENERAL_ERROR
            response.status, message, res = check_error(sockcli, SeqNo, sleep_counter, res)        

        if  not res:
            res = {"zone": -1, "lead_time": -1}

        sys.stdout.write("%s: zone=%s lead time=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), res["zone"], res["lead_time"]) )     
    except Exception as e:
        print 'Exception in get_zone_by_gps 2', str(e)

    sockcli.lock.acquire()
    del sockcli.ITaxiSrvReqDic[SeqNo]
    sockcli.lock.release()

    return res      

#object
def get_server_pickup_time(zone_info):
   zone_timeout = get_server_time()
   if 'lead_time' in zone_info and zone_info['lead_time'] > -1:
        zone_timeout += datetime.timedelta(minutes=zone_info["lead_time"])
   return zone_timeout

#object
def get_server_default_immediate_time():
    zone_timeout = get_server_time()   
    zone_timeout += datetime.timedelta(minutes=Config.DefaultZoneTimeout)
    return zone_timeout

#object
def get_server_time():
    return datetime.datetime.now()

'''
    Returns a string
'''
#string
def get_default_server_time():
    return (datetime.datetime.strftime(datetime.datetime.now(), Config.DateFormat_SaveOrder_Input))


def send_general_error(response):
    response.headers["Content-type"] = "application/json"
    response.status = 500
    res = {'status': response.status, 'result': { 'message': 'failure'}}
    return json.dumps(res)


def check_zone(sockcli, dic):
    zone_info = {}
    res={}
    status = 200

    try:
        #print dic
        if dic.has_key("pick_up_zone"):
            zone_info["zone"] = dic["pick_up_zone"]

        elif dic.has_key("pick_up_lat") and dic.has_key("pick_up_lng") and dic.has_key("fleet_number"):
            
            zone_info = get_zone_by_gps(sockcli, dic["pick_up_lat"], dic["pick_up_lng"], dic["fleet_number"])
            if (zone_info["zone"] == -1 and zone_info["lead_time"] == -1 ):
                sys.stdout.write("%s: can not get zone \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
                status = 500
                res = {"status": status, "result": {"message": ErrorMsg.ERROR_MSG_CANNOT_ZONE, "job_number": -1, "fare_type": "", "zone": ''} }
        else:
            zone_info["zone"] = -1
            sys.stdout.write("%s: can not get zone \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)) ) 
            status = 500
            res = {"status": status, "result": {"message": 'INVALID ZONE', "job_number": -1, "fare_type": "", "zone": ''} }
    
    except Exception as e:
        pass

    #print zone_info
    return status, zone_info, res

'''
if the flag is not in the dic, we do not care
if the flag is passed on, we must return :
    error (false) if it is not set
    success (true) if he param is set
'''
def is_flat_fare(dic):
    try:
        is_ok = True
        if 'is_flat_rate' in dic and dic['is_flat_rate'] in ('Y', 'y', 'T', 't'):
            return scap_funcs.is_flat_fare_on()
        else:
            return is_ok
    except Exception as e:
        pass

    return is_ok

def get_request_params():
    try:
       
        for l in request.body:
            print 'Request  %s ' % ( l )


        res={}

        mykeys = ['REMOTE_ADDR', 'REMOTE_PORT']
        for k in mykeys:
            if k in request.environ:
                res[k] = request.environ[k]
       
        print res

    except Exception as e:
        print 'get_request_params %s' % ( str(e))
        pass
