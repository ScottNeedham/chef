
# coding=utf-8
from gevent import monkey; monkey.patch_all()
import gevent 

from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import datetime
import json
import sys
import time
import socketcli
import socket
import thread
import config.cwebsconf as Config
import format_field
import dblayer
import validpr
import msgconf
import errormsg as ErrorMsg
import server_utils as Utils

import scap as scap_manager
import itertools



def send_success(res_dic):
    try:
        res = {}

        #res.update (res_dic)
        response.status = 200
        res['status'] = response.status
        res['result'] = res_dic     
    except Exception as e:
        return res

    return res

def _get_sys_params():
    try:
   
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response =  Utils.prepare_header('_get_sys_params', "default")
        if response.status == 401:
            return 

        response.status = 500
        Utils.set_default_headers(response)
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}

        clen = request.content_length
        request.body.seek(0)

        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 
            __name__, 
            str(dic) ))

        except Exception as e:
            print 'Exception: ', str(e)
            Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)

        if 'read_param' in dic: 

            try: 
                res['result']['params'] = []               
               
                if type ( dic['read_param']) == list:                  
                    for item in  dic['read_param'] :                                               
                        param_type = scap_manager.SCAP_SYS_PARAM 
                        if 'param_type' in item and item['param_type'] == "app_param":
                            param_type = scap_manager.SCAP_APP_PARAM                                 
                        
                        rsp = read_param(item['param_number'], param_type)
                        
                        res['result']['params'].append(rsp)
                        
                else:
                    param_type = scap_manager.SCAP_SYS_PARAM
                    if 'param_type' in dic['read_param'] and dic['read_param']['param_type'] == "app_param":
                        param_type = scap_manager.SCAP_APP_PARAM 
                                
                    rsp = read_param(dic['read_param']['param_number'], param_type)                  

                    res['result']['params'] =rsp


                print  res['result']['params']
                
                res['result']['params'] =  flatten_lists( res['result']['params'] )      

                response.status = 200  
                res["result"]["message"] =  "success"
                res.update( {"status": response.status} )
                return json.dumps(res)
                
            except Exception as e:
                sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))   
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
        else:
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
         
    except Exception as e:
        print 'Exception: ', str(e)
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)


    except Exception as e:
        return res

    return res    


def read_param(dic, param_type):
    res=None
    try:
        try:
            if type(dic) == list: 
                res =[]               
                for item in dic:
                    if type(item) == int:                        
                        rsp = scap_manager.read_scap_parameter(item, param_type)                                 
                        res.append(rsp)
            else:
                item = dic
                if type(item) == int:
                    rsp = scap_manager.read_scap_parameter(item, param_type)
                    res = rsp
                
        except Exception as e:
            sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))   
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)

    except Exception as e:
        return res

    return res



def flatten_lists(inlist):
    try:        
        out=[]
        if isinstance(inlist, list): 
            for i in inlist:     
                if isinstance(i, list): 
                    for j in i:                         
                        out.append(j)
                else:
                    out.append(i)
        else:
            return inlist

    except Exception as e:
        sys.stdout.write("%s: flatten_lists Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))           
        return inlist

    return out


#"SP_flat_rate_tag_in_fare_details" : 1346
def is_flat_fare_on():
    try:
        is_on = False
        res_dic = scap_manager.read_scap_parameter(1346)
        print res_dic
        if res_dic and "param_val" in res_dic:
            if res_dic["param_val"] > 0:
                is_on = True
            else:
                is_on = False                   
    except Exception as e:
        sys.stdout.write("%s: _is_flate_fare_on Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))           
        return is_on

    return is_on


#"SP_fleet_related_op_on" : 683
def _get_fleet_separation():

    response.status = 500
    Utils.set_default_headers(response)

    res = {'status': response.status, 'result': 'failure'}


    res_dic = scap_manager.read_scap_parameter(683)
    if res_dic:       
        res = send_success(res_dic)
    return res


#"SP_multi_fleet_zoning_on" : 809
def _get_fleet_related_op():

    response.status = 500
    Utils.set_default_headers(response)
    res = {'status': response.status, 'result': 'failure'}


    res_dic = scap_manager.read_scap_parameter(809)
    if res_dic:
        if res_dic["sp_param_val"] == 1:
            on_off = 'ON' 
        res.update (res_dic)
        response.status = 200
        res['status'] = response.status
        res['result'] = 'success'             

    return res


#"SP_q_sizes_as_MDT_Group on" : 810
def _get_q_sizes_as_MDT_Group():

    response.status = 500
    Utils.set_default_headers(response)

    res = {'status': response.status, 'result': 'failure'}


    res_dic = scap_manager.read_scap_parameter(810)
    if res_dic:
        if "sp_param_val" in res_dic :
            res['param_value'] = res_dic["sp_param_val"]

        res.update (res_dic)
        response.status = 200
        res['status'] = response.status
        res['result'] = 'success'  

    return res


#"SP_bailout_dispatch_call_on" : 1276,
def _get_bailout_dispatch_call_on():

    response.status = 500
    Utils.set_default_headers(response)

    res = {'status': response.status, 'result': 'failure'}


    res_dic = scap_manager.read_scap_parameter(1276)
    if res_dic:

        if res_dic["sp_param_val"] == 1:
            on_off = 'ON' 
   
        res.update (res_dic)
        response.status = 200
        res['status'] = response.status
        res['result'] = 'success'       

    return res

#"SP_bailout_code_value" : 1277,
def _get_bailout_code_value():

    response.status = 500
    Utils.set_default_headers(response)

    res = {'status': response.status, 'result': 'failure'}


    res_dic = scap_manager.read_scap_parameter(1277)
    if res_dic:
        if res_dic["sp_param_val"] == 1:
            on_off = 'ON'     
        res.update (res_dic)
        response.status = 200
        res['status'] = response.status
        res['result'] = 'success'       
    return res

#APP PARAMS
def _get_default_fleet():
    result = False
    try:
        response.status = 500

        Utils.set_default_headers(response)
        
        res = {'status': response.status, 'result': 'failure'}

        res_dic = read_scap_parameter(139, SCAP_APP_PARAM)
        if res_dic:
           if res_dic["sp_type"] == SCAP_PARAM_TYPE_NUMERIC and res_dic["sp_param_val"] == 1:
               result = True 
 
    except Exception as e:
        return result
    
    return result


