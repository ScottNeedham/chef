
# coding=utf-8
from gevent import monkey
monkey.patch_all()


from bottle import request, response
import datetime
import json
import sys

import config.cwebsconf as Config

import errormsg as ErrorMsg
import server_utils as Utils

import files.system_limits as system_limits


PARAM_IDS = [ 21 ]
PARAM_NAMES = [ 'taxi_supv']

def send_success(res_dic):
    try:
        res = {}

        response.status = 200
        res['status'] = response.status
        res['result'] = res_dic     
    except Exception as e:
        return res

    return res

def _get_sys_limit_param():
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response = Utils.prepare_header('_get_sys_limit_param', "default")
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
                __name__, str(dic)))

        except Exception as e:
            print 'Exception: ', str(e)
            Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)

        if 'param_action' in dic and 'param_id' in dic:
            try:
                param_id = -1
                if type(dic['param_id']) == int and dic['param_id'] in PARAM_IDS:
                    param_id = dic['param_id']
                elif type(dic['param_id']) in [str, unicode] and dic['param_id'] in PARAM_NAMES:
                    param_id = 21
                if dic['param_action'] not in ['read', 'write']:
                    res["result"]["message"] = "param_action must be either 'read' or 'write'"
                    return json.dumps(res)
                if param_id != -1 and dic['param_action'] in ['read']:
                    res, sl = system_limits.read_system_limits(param_id=param_id)
                    if res["result"] != -1:
                        response.status = 200
                        res = {"status": response.status, "result": {"message": "success", "taxi_supv": chr(sl.taxi_supv) } }
                else:
                    return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)            

                return json.dumps(res)
            except Exception as e:
                sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))   
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
        else:
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)

    except Exception as e:
        sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))           
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)


    except Exception as e:
        sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))           
        return res

    return res


#"taxi_supv" : 21
def _get_taxi_supv():

    response.status = 500
    Utils.set_default_headers(response)

    res = {'status': response.status, 'result': 'failure'}

    res_dic = system_manager.read_system_limits(param_id=21)
    if res_dic:
        res = send_success(res_dic)
    return res


# "taxi_supv" : 21
def _set_taxi_supv(value=None):
    response.status = 500
    res = {'status': response.status, 'result': 'failure'}

    if value == '' or value not in ['V', 'S']:
        res['result'] = "Invalid parameter value."
        return res
    try:
        Utils.set_default_headers(response)
        res_dic = system_manager.write_system_limits(param_id=21,
                                                    param_val=value)
        if res_dic:
            res = send_success(res_dic)
        return res

    except Exception as e:
        sys.stdout.write("%s: Exception in %s \n"
                            % (datetime.datetime.strftime
                            (datetime.datetime.now(),
                            Config.LOG_DATETIME_FORMAT),
                            str(e)))
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
    return res
