
# coding=utf-8
from gevent import monkey; monkey.patch_all()
import gevent 

from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import datetime
import json
import sys
import time
import zqqwrap
import smalldb
import socketcli
import socket
import thread
import config.cwebsconf as Config
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
import errormsg as ErrorMsg
import vehicle_msg
import server_utils as Utils
import supervisor_message as SupervisorMsg
import cabmate_messenger;

import fleet_manager
from build.build import VERSION


def _get_version():
    response.status = 200
    response.headers["Content-type"] = "application/json"
    res = {'status': response.status, 'result': {'version': VERSION}}
    return res


def _get_hostinfo():
    print __name__
    print 'cwebs_hostinfo environment: ', request.environ
   

    response =  Utils.prepare_header('get_cwebs_hostinfo', "default")
    if  response.status == 401:
        return            

    response.headers["Content-type"] = "application/json"
    response.status = 500
    res = {'status': response.status, 'result': {'message': 'failure'}}
    
    lFleetSeparation = False
    try:
        lres = scap.is_fleet_separation_on()
        if lres == True:
            lFleetSeparation = True 
    except Exception as e:
        print 'Exception ', str(e) 
        return res
    response.status = 200
    res = {'status': response.status, 'result': {'fleet_separation': lFleetSeparation}}
    return res


def _fleet_send_msg():
    try:
        res= {}
        
      
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response =  Utils.prepare_header('send_fleet_msg', "default")
        if response.status == 401:
            return 
        #print str(request)
        #print str(request.body)
        response.status = 500
        response.headers["Content-type"] = "application/json"
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

        if all (k in dic for k in ('operator_id', 'fleet')): 

            try:
                vehmsg = vehicle_msg.VehicleMessage(dic, msgconf.FLEET_MSG)

                if vehmsg.getError() == False:
                    print 'Sending a request to Fleet '
                    r =   vehmsg.send_driver_msg(dic) 
                    print 'Logging Fleet message ...'
                    
                    vehmsg.createLogEntry(dic)
                else:
                    print  'Error with object ...'
                    return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_SENDING_FLEET_MSG)
                 
                return Utils.make_error_response(response, 200, "success")
                

            except Exception as e:
                print 'Exception in fleet_send_msg ', str(e)
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
               
        else:

            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
         
    except Exception as e:
        print 'Exception: ', str(e)
        sys.stdout.write("%s: exiting %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)



def _clear_device_emergency():
    try:
        res= {}
      
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response =  Utils.prepare_header('clear_device_emergency', "default")
        if response.status == 401:
            return 
        #print str(request)
        #print str(request.body)
        response.status = 500
        response.headers["Content-type"] = "application/json"
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
            sys.stdout.write("%s: Could not decode JSON - Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))  
            Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)

        if 'taxi' and 'fleet' in dic: 
            try:
                dic['action'] =  "EmergencyClear"                      
                cabmsg = cabmate_messenger.CabmateMessenger(dic)

                err, errmsg = cabmsg.get_error() 
                if err == False:
                    sys.stdout.write("%s: Sending clear emergency msg \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))                                       
                    cabmsg.send_hello()                                              
                    r =   cabmsg.send_msg(dic)                           
                    cabmsg.send_goodbye()
                else:
                    if errmsg == None:
                        errmsg = ErrorMsg.ERROR_MSG_EMERGENCY_CLEAR

                    sys.stdout.write("%s: Error %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), errmsg ))                        
                    return Utils.make_error_response(response, 500, errmsg)

                return Utils.make_error_response(response, 200, "success")
                

            except Exception as e:
                sys.stdout.write("%s: Exception in %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))   
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)
               
        else:

            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
         
    except Exception as e:
        print 'Exception: ', str(e)
        return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)


def _vehicle_send_msg():
    try:
        res= {}
        

        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        response =  Utils.prepare_header('vehicle_send_msg', "default")
        if response.status == 401:
            return 
        #print str(request)
        #print str(request.body)
        response.status = 500

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
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)


        #print 'dic ', dic
       
        if all (k in dic for k in ('operator_id', 'taxi')):
            try:
                if isinstance(dic, dict):
                    vehmsg = vehicle_msg.VehicleMessage(dic, msgconf.VEHICLE_MSG)

                    if isinstance(vehmsg, vehicle_msg.VehicleMessage):
                        if vehmsg.getError() == False:
                            print 'Sending a request to vehicle '
                            r =   vehmsg.send_driver_msg(dic) 
                            print 'Logging ...'
                    
                            vehmsg.createLogEntry(dic)
                                                    
  
                            response.status = 200
                            resp_message = "success"
                            res = {'status': response.status, 'result': {'message':   resp_message}}
                            print json.dumps(res)

                        else:
                            print  'Error with object ...'
                            
                            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_INVALID_DRIVER_ID)
                    else:
                        print 'Could not create object'
                else:
                    res = {'status': response.status, 'result': {'message': 'ERROR'}}    


            except Exception as e:
                print 'Exception in  vehicle_send_msg', str(e)
             
                return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)
               
        else:
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
         

    except Exception as e:
        print 'Exception vehicle_send_msg: ', str(e)
        return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)
   
    return json.dumps(res)


def _driver_send_msg():
    try:
        res= {}


        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), 'driver_send_msg'))
        response =  Utils.prepare_header('driver_send_msg', "default")
        if response.status == 401:
            return 
       
        response.status = 500

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
            sys.stdout.write("%s: Exception in driver_send_msg %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)

        #print 'dic ', dic
       
        if all (k in dic for k in ('operator_id', 'driver_id')):

            try:
                if isinstance(dic, dict):
                   
                    vehmsg = vehicle_msg.VehicleMessage(dic, msgconf.DRIVER_MSG)
                  

                    if isinstance(vehmsg, vehicle_msg.VehicleMessage):
                                               
                        if vehmsg.getError() == False:
                            
                            veh = vehmsg.findVehicle(dic['driver_id'])
                            if 'vehicle_number' in veh:
                                if veh["vehicle_number"] is not None:
                                    dic['taxi'] = veh["vehicle_number"] 
                                    print '  Found ', veh["vehicle_number"] 
                                    print 'Sending a request to driver '
                                    r =   vehmsg.send_driver_msg(dic) 
                                    print 'Logging ...'
                    
                                    vehmsg.createLogEntry(dic)
                                
                                    return Utils.make_error_response(response, 200,  "success")

                                else:
                                    return Utils.make_error_response(response, 500, 'Could not find vehicle in DB for driver')     
                            
                            else:
                                return Utils.make_error_response(response, 500, 'Could not locate vehicle for driver')
                                
                        else:
                            print  'Error with object ...'
                            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_INVALID_DRIVER_ID)
                            
                    else:
                        print 'Could not create object'
                else:
                    res = {'status': response.status, 'result': {'message': 'ERROR'}}    


            except Exception as e:
                print 'Exception in  vehicle_send_msg', str(e)
                
                return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)
               
        else:
            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
          
    except Exception as e:
        print 'Exception driver_send_msg: ', str(e)
    
        return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_REQUEST_READ)
   
    return json.dumps(res)

def _dispatch_queues():
    try:
        print __name__
        print 'dispatch_queues environment: ', request.environ
      

        response =  Utils.prepare_header('dispatch_queues', "default")
        if  response.status == 401:
            return            

        print 'dispatch_queues: HMAC is verified...'
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        clen = request.content_length
        request.body.seek(0)
        try:
            msg_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: msg_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(msg_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res) 
              
        response.status = 200
        res = {'status': response.status, 'result': {'message': 'success'}}
        return json.dumps(res)
    except Exception as e:
        print "dispatch_queues: Exception %s" % (str(e))
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)


def _driver_action(data_src):
    try:
        driver_dic = {}
        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: driver action %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))
      

        response =  Utils.prepare_header('driver_action', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)

        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': { 'message': 'failure'}}
        try:
            action_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: action dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(action_dic) ))
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)  
            
        if not action_dic.has_key('db_action_id'):
            res['result']['message'] = 'failure: db_action_id field is missing'
            return json.dumps(res)
        try:
            db_action_id = int(action_dic["db_action_id"])
        except Exception as e:
            res['result']['message'] = 'failure: invalid db_action_id'
            return json.dumps(res)
   
        if not action_dic.has_key('msg_id'):
            res['result']['message'] = 'failure: msg_id field is missing'
            return json.dumps(res)
        try:
            msg_id = int(action_dic["msg_id"])
        except Exception as e:
            res['result']['message'] = 'failure: invalid msg_id'
            return json.dumps(res)

        if not action_dic.has_key('action'):
            res['result']['message'] = 'failure: action field is missing'
            return json.dumps(res)
        if not action_dic['action'] in ["delete", "add", "modify", "update"]:
            res['result']['message'] = 'failure: invalid action field value'
            return json.dumps(res)

        if not action_dic.has_key('driver_id'):
            res['result']['message'] = 'failure: driver_id field is missing'
            return json.dumps(res)
        try:
            driver_id = int(action_dic['driver_id'])
        except Exception as e:
            res['result']['message'] = 'failure: driver_id field is not int'
            return json.dumps(res)
        
        if action_dic['action'] == "delete":
            print 'sending message to delete driver'   
            driver.delete_driver(driver_id)
        elif action_dic['action'] == "add" or action_dic['action'] == "modify" or action_dic['action'] == "update":
            try:
                driver_dic = dblayer.get_driver_info(data_src, driver_id)
            except Exception as e:
                sys.stdout.write("%s: exception is raised in driver action %s (dblayer) \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
                return Utils.send_general_error(response)

            try:
                drv = driver.DriverParams(driver_dic, action_dic['action'])
            except Exception as e:
                sys.stdout.write("%s: exception is raised in driver action (1) \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
                return Utils.send_general_error(response)

            print 'sending message to add or modify driver' 
            drv.add_modify_driver(action_dic['action'])   
        response.status = 200
        res = {'status': response.status, 'result': {'message': 'success'}}
        return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: exception is raised in driver action %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
        return Utils.send_general_error(response)
        

def _vehicle_action(data_src):
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: vehicle action %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))
      

        response =  Utils.prepare_header('vehicle_action', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': { 'message': 'failure'}}
        try:
             action_dic = json.loads(str(request.body.read(clen)))
             sys.stdout.write("%s: action dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(action_dic) ))
        except Exception as e:
             print 'Exception ', str(e)
             return json.dumps(res)

        if not action_dic.has_key('db_action_id'):
            res['result']['message'] = 'failure: db_action_id field is missing'
            return json.dumps(res)
        try:
            db_action_id = int(action_dic["db_action_id"])
        except Exception as e:
            res['result']['message'] = 'failure: invalid db_action_id'
            return json.dumps(res)
   
        if not action_dic.has_key('msg_id'):
            res['result']['message'] = 'failure: msg_id field is missing'
            return json.dumps(res)
        try:
            msg_id = int(action_dic["msg_id"])
        except Exception as e:
            res['result']['message'] = 'failure: invalid msg_id'
            return json.dumps(res)

        if not action_dic.has_key('action'):
            res['result']['message'] = 'failure: action field is missing'
            return json.dumps(res)
        if not action_dic['action'] in ["delete", "add", "modify", "update", "suspend", "reinstate"]:
            res['result']['message'] = 'failure: invalid action field value'
            return json.dumps(res)

        if not action_dic.has_key('vehicle_id'):
            res['result']['message'] = 'failure: vehicle_id field is missing'
            return json.dumps(res)
        try:
            vehicle_id = int(action_dic['vehicle_id'])
        except Exception as e:
            res['result']['message'] = 'failure: vehicle_id field is not int'
            return json.dumps(res)
        if action_dic['action'] in ["suspend", "reinstate"]:
            if action_dic['action'] == "suspend":
                duration = 1
                try: 
                    duration = int(action_dic['duration'])
                    if duration < 1 or duration > 24: 
                        duration = 1
                except Exception as e:
                   pass 
                if not action_dic.has_key('msg_for_dispatch'):
                    res['result']['message'] = 'failure: message for dispatch is not present'
                    return json.dumps(res)
                msg_for_dispatch = str(action_dic["msg_for_dispatch"])
                if len(msg_for_dispatch) > 32:
                    msg_for_dispatch = msg_for_dispatch[:32]

                if not action_dic.has_key('msg_for_driver'):
                    res['result']['message'] = 'failure: message for driver is not present'
                    return json.dumps(res)
                msg_for_driver = str(action_dic["msg_for_driver"])
                if len(msg_for_driver) > 32:
                    msg_for_driver = msg_for_driver[:32]

                dData = (vehicle_id, duration, long(time.time()), 
                    msgconf.CWEBS, 
                    msg_for_dispatch, 
                    msg_for_driver,  '1', '2', 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*' ', 0)
                print 'dData ', dData
                s = struct.Struct('I I I I 33s 33s c c 3I 16I 4s I')  #  suspension data
                packed_data = s.pack( *dData)
                data_size = s.size
                print 'datasize (should be 168) ', data_size                
                ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
                cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_SUSP_TAXI, ss)
            if action_dic['action'] == "reinstate":
                s = struct.Struct('I')  #  suspension data
                dData = (vehicle_id, )
                packed_data = s.pack( *dData)
                data_size = s.size              
                ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
                cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_REINST_TAXI, ss)
 
        if action_dic['action'] == "delete":
            print 'sending message to delete vehicle'  
            myveh = vehicle.VehicleParams()
            myveh.delete_vehicle(vehicle_id)
        if action_dic['action'] == "add" or action_dic['action'] == "modify" or action_dic['action'] == "update":
            vehicle_dic = dblayer.get_vehicle_info(data_src, vehicle_id)
            print 'vehicle_dic ', vehicle_dic
            if vehicle_dic["vehicle_number"] == -1:
                res['result']['message'] = 'failure: invalid vehicle id'
                return json.dumps(res)
            if vehicle_dic["fleet"] == 0:
                res['result']['message'] = 'failure: invalid fleet'
                return json.dumps(res) 
            if vehicle_dic.has_key("duplicate_alias_vehicle_id"):
                if vehicle_dic["duplicate_alias_vehicle_id"] > 0: 
                    res['result']['message'] = 'failure: alias is not unique vehicle ' + str(vehicle_dic["duplicate_alias_vehicle_id"]) 
                    return json.dumps(res)
            if vehicle_dic.has_key("duplicate_long_alias_vehicle_id"):
               if vehicle_dic["duplicate_long_alias_vehicle_id"] > 0:
                    res['result']['message'] = 'failure: long alias is not unique vehicle ' + str(vehicle_dic["duplicate_long_alias_vehicle_id"])
                    return json.dumps(res)
            veh = vehicle.VehicleParams(vehicle_dic)
            print 'preparing data to add or modify vehicle'
            dData, dData0 = veh.vehicle_info_to_tuple()
            print dData, dData0
            #veh.add_modify_vehicle(action_dic['action'])   
            s = struct.Struct('4I 71h 2c 4s 24s 4s 2c 2s 10h 12I 16s 2c 2s 2I 28s')   # taxi info data
            packed_data = s.pack( *dData)
            data_size = s.size 
            ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
            if action_dic['action'] == 'add':
                print 'sending message to add vehicle'
                cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_ADD_TAXI, ss)
            if action_dic['action'] in ['update', 'modify']:
                print 'sending message to update vehicle' 
                cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_MODTAXINFO, ss)              
            s = struct.Struct('h 9s 20s 20s')   # extended taxi info data
            packed_data = s.pack( *dData0)
            data_size = s.size
            ss = struct.Struct(cabmsg.base_fmt + '%ds' % (s.size))  
            cabmsg.gmsg_send(packed_data, data_size, msgconf.TFC, 0, msgconf.MT_EXTENDED_TAXI_INFO, ss)
        response.status = 200
        res = {'status': response.status, 'result': {'message': 'success'}}
        return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: exception is raised in vehicle action\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        print "vehicle action: Exception %s" % (str(e))
        res['result']['message'] = 'failure: Exception ' + str(e) 
        return json.dumps(res)     
        

def _device_sendmsg(sockcli):
    try:
        sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: device sendmsg %s\n" % (
        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(request.environ) ))
       
        response =  Utils.prepare_header('device_sendmsg', "default")
        if  response.status == 401:
            return            

        clen = request.content_length
        request.body.seek(0)
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        try:
            sendmsg_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: sendmsg_dic %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(sendmsg_dic) ))
        except Exception as e:
            print 'Exception while retrieving the JSON data', str(e)
            return json.dumps(res)
        try:
            taxi_no = int(sendmsg_dic["vehicle_id"])
            taxi_no_str =  format_field.format_field(str(taxi_no), 6, True)
        except Exception as e:
            res['result'] = {'message': 'invalid vehicle_id'}
            return json.dumps(res)

        # constructing envelop
        SeqNo = sockcli.generate_SeqNo()
        # messageid
        itaxmsgid = '670144'
        try: 
            msgtext = sendmsg_dic["msgtext"] if sendmsg_dic["msgtext"] else "text message to " + taxi_no_str
        except Exception as e: 
            res['result'] = {'message': 'invalid msgtext'}
            return json.dumps(res)
            
        message = itaxmsgid + SeqNo + taxi_no_str + format_field.format_field(msgtext, 128, True)
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
            gevent.sleep(1)
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
        sys.stdout.write("%s: device sendmsg terminated due to exception\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status, 'result': {'message': 'failure'}}
        return json.dumps(res)


def _zone_by_gps(sockcli):
    try:
   
        response =  Utils.prepare_header('zone_by_gps', "default")
        if  response.status == 401:
            return

        response.status = 500
        response.headers["Content-type"] = "application/json"
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        clen = request.content_length
        request.body.seek(0)
        try:
            zone_dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(zone_dic) ) )
        except Exception as e:
            print "Exception ", str(e)
            res["result"] = {"message": ErrorMsg.ERROR_MSG_REQUEST_READ}
            return json.dumps(res)
         
        try:
            lon = float(zone_dic["lon"])
            lat = float(zone_dic["lat"])
            if abs(lat) > 90.000001 or abs(lon) > 180.000001 or abs(lat) + abs(lon) < 0.000001:
                raise Exception(ErrorMsg.ERROR_MSG_INVALID_GPS)
        except Exception as e:
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_GPS}
            return json.dumps(res)
        try:
            fleetnum = int(zone_dic["fleet"])
            if fleetnum < 0 or fleetnum > 99999:
                raise Exception(ErrorMsg.ERROR_MSG_INVALID_FLEET)
        except Exception as e:
            res["result"] = {"message": ErrorMsg.ERROR_MSG_INVALID_FLEET}
            return json.dumps(res)
        
        res = Utils.get_zone_by_gps(sockcli, lat, lon, fleetnum)
        return json.dumps(res)

      
    except Exception as e:
        response.status = 500
        res = {"status": response.status, "result": {"message": ErrorMsg.ERROR_MSG_GENERAL_ERROR}}
        return json.dumps(res)


def _get_driver_suspend_list():
    try:
        #sys.stdout.write("%s: entering %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__))
        sys.stdout.write("%s: get_driver_suspend_list %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))
       
        response =  Utils.prepare_header('get_driver_suspend_list', "default")
        if  response.status == 401:
            return            

        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_drivers': 0, 'drivers': []}
        }
        file_name = "/data/drivsusp.fl"
        try:
            fp = open(file_name, "r")
            fp.close()
        except Exception as e:
            print 'Exception ', str(e)
            return json.dumps(res)

        '''
        driver_id As Long
        susp_duration As Long
        susptime As Long
        oper_id As Integer
        reason1 As String * 33
        reason2 As String * 33
        comp_num As Byte
        spare As Byte
        taxi As Integer
        fleet As Integer
        LimitReinstate As String * 1
        junk As String * 9
        If DrSuspRec.susp_duration <> 0 Then
            txtHours = DrSuspRec.susp_duration Mod 1000
            txtMins = DrSuspRec.susp_duration \ 1000
        Else
            txtHours = ""
            txtMins = ""
        End If
        '''
        ################################################
        # this is suspension structure 
        # s = struct.Struct('I I I h 33s 33s c c h h 8s')
        # we need 2 bytes for padding, hence 10s
        ################################################ 
        frmt = 'i i I h 33s 33s c c h h 10s'
        s = struct.Struct(frmt)
        print 'structure size of driver suspend record', s.size
        drivers = []
        number_of_drivers = 0
        try:
            counter = 0
            print 'opening file ', file_name
            fp = open(file_name, "r")
            while True:
                counter = counter + 1
                data = fp.read(s.size)
                if data:
                    tmp = struct.unpack(frmt, data)
                    print 'record ', counter, tmp 
                    if tmp[0] > 0:
                        susp_time = susp_time_m = susp_time_h = 0
                        if tmp[1] > 0:
                            try:
                                susp_time_h = tmp[1] % 1000
                                susp_time = susp_time_h
                                susp_time_m = int(tmp[1] / 1000)
                            except Exception as e:
                                pass
                            number_of_drivers = number_of_drivers + 1
                            drivers.append({"driver_id": tmp[0], 
                                "suspension_time": susp_time,
                                "suspension_time_min": susp_time_m,
                                "suspension_timestamp": tmp[2]})
                    else:
                        break
                else:
                    sys.stdout.write("%s: No data returned in get_driver_suspend_list...\n" % ( 
                        datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
                    break;
                         
            fp.close()
            response.status = 200
            res = {'status': response.status,
                   'result': {'message': 'OK', 'number_of_drivers': number_of_drivers, 'drivers': drivers}
            }
            #print json.dumps(res)
            return json.dumps(res)
        except Exception as e:
            print "get_driver_suspend_list: Exception %s" % (str(e))
            return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: returning out of handler get_driver_suspend_list...\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
        #print "get_driver_suspend_list: Exception %s" % (str(e))
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_drivers': 0, 'drivers': []}}
        return json.dumps(res)


def _modify_fleet():
    try:
        sys.stdout.write("%s: modify_fleet %s\n" % (
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
            str(request.environ) ))
       
        response =  Utils.prepare_header('modify_fleet', "default")
        if  response.status == 401:
            return            

        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure'}
        }       

        clen = request.content_length
        request.body.seek(0)
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': { 'message': 'failure'}}
        try:
            dic = json.loads(str(request.body.read(clen)))
            sys.stdout.write("%s: dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),
                str(dic) ))
        except Exception as e:
             print 'Exception ', str(e)
             return json.dumps(res)
   
        if 'action' not in dic :
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_MISSING_ACTION_FIELD)

        if  dic['action'] not in [ 'modify' ]:
            return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_UNSUPPORTED_ACTION)

        if all (k in dic for k in ('name', 'fleet')): 
            try:
                dic["action_id"] = msgconf.MT_MODFLEETINFO
                fleetmgr = fleet_manager.FleetManager(dic)

                if fleetmgr.get_error() == False:
                    print 'Sending fleet request ...'
                    r =   fleetmgr.send_msg(dic)  
                    return  r
                else:
                    print  'Error with object ...'
                    return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_SENDING_FLEET_MSG)
                 
                return Utils.make_error_response(response, 200, "success")              

            except Exception as e:
                print 'Exception in modify_fleet ', str(e)
                return Utils.make_error_response(response, 500, ErrorMsg.ERROR_MSG_REQUEST_READ)               
        else:

            return Utils.make_error_response(response, 500,  ErrorMsg.ERROR_MSG_MISSING_MANDATORY_FIELD)
        if ['number', 'name'] not in dic:
            res['result']['message'] = 'failure: mandatory field is missing'
            return json.dumps(res)
       

            return json.dumps(res)

    except Exception as e:
        sys.stdout.write("%s: returning out of handler modify_fleet ...\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ))
    
        response.headers["Content-type"] = "application/json"
        response.status = 500
        res = {'status': response.status,
               'result': {'message': 'failure'}
              }
        return json.dumps(res)      
